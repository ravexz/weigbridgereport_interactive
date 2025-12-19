import sqlite3
import os

DB_PATH = "reports.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create Lookup Tables
    cursor.execute("CREATE TABLE IF NOT EXISTS zones (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, reg_number TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS clerks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS routes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, zone_id INTEGER, FOREIGN KEY(zone_id) REFERENCES zones(id))")
    
    # 2. Check if migration is needed (if daily_entries has text fields instead of IDs)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_entries'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        try:
            # Check for old column 'zone' (text) vs new 'zone_id'
            cursor.execute("PRAGMA table_info(daily_entries)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'zone' in columns and 'zone_id' not in columns:
                print("Migrating database to normalized schema...")
                
                # A. Migrate Data to Lookups
                cursor.execute("SELECT DISTINCT zone FROM daily_entries WHERE zone IS NOT NULL AND zone != ''")
                for row in cursor.fetchall():
                    cursor.execute("INSERT OR IGNORE INTO zones (name) VALUES (?)", (row[0].upper(),))
                    
                cursor.execute("SELECT DISTINCT vehicle FROM daily_entries WHERE vehicle IS NOT NULL AND vehicle != ''")
                for row in cursor.fetchall():
                    cursor.execute("INSERT OR IGNORE INTO vehicles (reg_number) VALUES (?)", (row[0].upper(),))
                    
                cursor.execute("SELECT DISTINCT clerk FROM daily_entries WHERE clerk IS NOT NULL AND clerk != ''")
                for row in cursor.fetchall():
                    cursor.execute("INSERT OR IGNORE INTO clerks (name) VALUES (?)", (row[0].upper(),))
                    
                cursor.execute("SELECT DISTINCT route, zone FROM daily_entries WHERE route IS NOT NULL AND route != ''")
                for row in cursor.fetchall():
                    route_name = row[0].upper()
                    zone_name = row[1].upper() if row[1] else None
                    zone_id = None
                    if zone_name:
                        cursor.execute("SELECT id FROM zones WHERE name=?", (zone_name,))
                        z_res = cursor.fetchone()
                        if z_res: zone_id = z_res[0]
                    cursor.execute("INSERT OR IGNORE INTO routes (name, zone_id) VALUES (?, ?)", (route_name, zone_id))

                # B. Rename Old Table
                cursor.execute("ALTER TABLE daily_entries RENAME TO daily_entries_old")
                
                # C. Create New Table
                create_new_daily_entries_table(cursor)
                
                # D. Copy Data with Lookups
                cursor.execute("SELECT * FROM daily_entries_old")
                old_rows = cursor.fetchall()
                # Get column indices from old table
                # id(0), date(1), zone(2), clerk(3), vehicle(4), route(5), ...
                
                for row in old_rows:
                    # Helper to get ID
                    def get_id(table, col, val):
                        if not val: return None
                        cursor.execute(f"SELECT id FROM {table} WHERE {col}=?", (val.upper(),))
                        res = cursor.fetchone()
                        return res[0] if res else None

                    z_id = get_id('zones', 'name', row[2])
                    c_id = get_id('clerks', 'name', row[3])
                    v_id = get_id('vehicles', 'reg_number', row[4])
                    r_id = get_id('routes', 'name', row[5])
                    
                    cursor.execute('''
                        INSERT INTO daily_entries 
                        (date, zone_id, clerk_id, vehicle_id, route_id, time_out, time_in, tare_time, fld_wgt, fact_wgt, scorch_kg, quality_pct, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row[1], z_id, c_id, v_id, r_id, row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
                
                # E. Cleanup
                cursor.execute("DROP TABLE daily_entries_old")
                print("Migration complete.")
                
        except Exception as e:
            print(f"Migration failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return
    else:
        # Create new table directly
        create_new_daily_entries_table(cursor)

    conn.commit()
    conn.close()

def create_new_daily_entries_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            zone_id INTEGER,
            clerk_id INTEGER,
            vehicle_id INTEGER,
            route_id INTEGER,
            time_out TEXT,
            time_in TEXT,
            tare_time TEXT,
            fld_wgt REAL,
            fact_wgt REAL,
            scorch_kg REAL,
            quality_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(zone_id) REFERENCES zones(id),
            FOREIGN KEY(clerk_id) REFERENCES clerks(id),
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY(route_id) REFERENCES routes(id)
        )
    """)

def get_or_create_id(cursor, table, col, val, extra_col=None, extra_val=None):
    if not val: return None
    val = val.upper().strip()
    cursor.execute(f"SELECT id FROM {table} WHERE {col}=?", (val,))
    row = cursor.fetchone()
    if row:
        return row[0]
    
    if extra_col and extra_val:
        cursor.execute(f"INSERT INTO {table} ({col}, {extra_col}) VALUES (?, ?)", (val, extra_val))
    else:
        cursor.execute(f"INSERT INTO {table} ({col}) VALUES (?)", (val,))
    return cursor.lastrowid

def save_entry(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Get/Create IDs
    z_id = get_or_create_id(cursor, 'zones', 'name', data.get('zone'))
    c_id = get_or_create_id(cursor, 'clerks', 'name', data.get('clerk'))
    v_id = get_or_create_id(cursor, 'vehicles', 'reg_number', data.get('vehicle'))
    # Populate route with zone_id context
    r_id = get_or_create_id(cursor, 'routes', 'name', data.get('route'), 'zone_id', z_id)

    # 2. Insert Entry
    cursor.execute('''
        INSERT INTO daily_entries 
        (date, zone_id, clerk_id, vehicle_id, route_id, time_out, time_in, tare_time, fld_wgt, fact_wgt, scorch_kg, quality_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['date'], z_id, c_id, v_id, r_id,
        data.get('time_out'), data.get('time_in'), data.get('tare_time'),
        data['fld_wgt'], data['fact_wgt'], data['scorch_kg'], data['quality_pct']
    ))
    conn.commit()
    conn.close()

def get_entries_by_date(date):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # JOIN to get text values
    query = """
        SELECT e.*, z.name as zone, c.name as clerk, v.reg_number as vehicle, r.name as route
        FROM daily_entries e
        LEFT JOIN zones z ON e.zone_id = z.id
        LEFT JOIN clerks c ON e.clerk_id = c.id
        LEFT JOIN vehicles v ON e.vehicle_id = v.id
        LEFT JOIN routes r ON e.route_id = r.id
        WHERE e.date=? 
        ORDER BY e.id ASC
    """
    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_entry(entry_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    z_id = get_or_create_id(cursor, 'zones', 'name', data.get('zone'))
    c_id = get_or_create_id(cursor, 'clerks', 'name', data.get('clerk'))
    v_id = get_or_create_id(cursor, 'vehicles', 'reg_number', data.get('vehicle'))
    r_id = get_or_create_id(cursor, 'routes', 'name', data.get('route'), 'zone_id', z_id)

    cursor.execute('''
        UPDATE daily_entries 
        SET zone_id=?, clerk_id=?, vehicle_id=?, route_id=?, 
            time_out=?, time_in=?, tare_time=?, 
            fld_wgt=?, fact_wgt=?, scorch_kg=?, quality_pct=?
        WHERE id=?
    ''', (
        z_id, c_id, v_id, r_id,
        data.get('time_out'), data.get('time_in'), data.get('tare_time'),
        data['fld_wgt'], data['fact_wgt'], data['scorch_kg'], data['quality_pct'],
        entry_id
    ))
    conn.commit()
    conn.close()

def get_entry_by_id(entry_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
        SELECT e.*, z.name as zone, c.name as clerk, v.reg_number as vehicle, r.name as route
        FROM daily_entries e
        LEFT JOIN zones z ON e.zone_id = z.id
        LEFT JOIN clerks c ON e.clerk_id = c.id
        LEFT JOIN vehicles v ON e.vehicle_id = v.id
        LEFT JOIN routes r ON e.route_id = r.id
        WHERE e.id=?
    """
    cursor.execute(query, (entry_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_entries():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
        SELECT e.*, z.name as zone, c.name as clerk, v.reg_number as vehicle, r.name as route
        FROM daily_entries e
        LEFT JOIN zones z ON e.zone_id = z.id
        LEFT JOIN clerks c ON e.clerk_id = c.id
        LEFT JOIN vehicles v ON e.vehicle_id = v.id
        LEFT JOIN routes r ON e.route_id = r.id
        ORDER BY e.date DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
