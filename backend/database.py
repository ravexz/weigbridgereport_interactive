import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database configuration - use environment variables in production
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'greenfield_reports'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Create Lookup Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zones (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY,
                reg_number VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clerks (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                zone_id INTEGER REFERENCES zones(id)
            )
        """)
        
        # 2. Create main entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_entries (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                zone_id INTEGER REFERENCES zones(id),
                clerk_id INTEGER REFERENCES clerks(id),
                vehicle_id INTEGER REFERENCES vehicles(id),
                route_id INTEGER REFERENCES routes(id),
                time_out VARCHAR(50),
                time_in VARCHAR(50),
                tare_time VARCHAR(50),
                fld_wgt DECIMAL(10, 2),
                fact_wgt DECIMAL(10, 2),
                scorch_kg DECIMAL(10, 2),
                quality_pct DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_entries_date ON daily_entries(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_entries_zone ON daily_entries(zone_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_entries_route ON daily_entries(route_id)")
        
        conn.commit()
        print("✅ PostgreSQL database initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_or_create_id(cursor, table, col, val, extra_col=None, extra_val=None):
    """Get existing ID or create new entry and return ID"""
    if not val:
        return None
    val = val.upper().strip()
    
    # Try to get existing
    cursor.execute(f"SELECT id FROM {table} WHERE {col}=%s", (val,))
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Create new
    if extra_col and extra_val:
        cursor.execute(
            f"INSERT INTO {table} ({col}, {extra_col}) VALUES (%s, %s) RETURNING id",
            (val, extra_val)
        )
    else:
        cursor.execute(
            f"INSERT INTO {table} ({col}) VALUES (%s) RETURNING id",
            (val,)
        )
    return cursor.fetchone()[0]

def save_entry(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Get/Create IDs
        z_id = get_or_create_id(cursor, 'zones', 'name', data.get('zone'))
        c_id = get_or_create_id(cursor, 'clerks', 'name', data.get('clerk'))
        v_id = get_or_create_id(cursor, 'vehicles', 'reg_number', data.get('vehicle'))
        r_id = get_or_create_id(cursor, 'routes', 'name', data.get('route'), 'zone_id', z_id)

        # 2. Insert Entry
        cursor.execute('''
            INSERT INTO daily_entries 
            (date, zone_id, clerk_id, vehicle_id, route_id, time_out, time_in, tare_time, 
             fld_wgt, fact_wgt, scorch_kg, quality_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['date'], z_id, c_id, v_id, r_id,
            data.get('time_out'), data.get('time_in'), data.get('tare_time'),
            data['fld_wgt'], data['fact_wgt'], data['scorch_kg'], data['quality_pct']
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def get_entries_by_date(date):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT e.*, z.name as zone, c.name as clerk, v.reg_number as vehicle, r.name as route
            FROM daily_entries e
            LEFT JOIN zones z ON e.zone_id = z.id
            LEFT JOIN clerks c ON e.clerk_id = c.id
            LEFT JOIN vehicles v ON e.vehicle_id = v.id
            LEFT JOIN routes r ON e.route_id = r.id
            WHERE e.date=%s 
            ORDER BY e.id ASC
        """
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()

def update_entry(entry_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        z_id = get_or_create_id(cursor, 'zones', 'name', data.get('zone'))
        c_id = get_or_create_id(cursor, 'clerks', 'name', data.get('clerk'))
        v_id = get_or_create_id(cursor, 'vehicles', 'reg_number', data.get('vehicle'))
        r_id = get_or_create_id(cursor, 'routes', 'name', data.get('route'), 'zone_id', z_id)

        cursor.execute('''
            UPDATE daily_entries 
            SET zone_id=%s, clerk_id=%s, vehicle_id=%s, route_id=%s, 
                time_out=%s, time_in=%s, tare_time=%s, 
                fld_wgt=%s, fact_wgt=%s, scorch_kg=%s, quality_pct=%s
            WHERE id=%s
        ''', (
            z_id, c_id, v_id, r_id,
            data.get('time_out'), data.get('time_in'), data.get('tare_time'),
            data['fld_wgt'], data['fact_wgt'], data['scorch_kg'], data['quality_pct'],
            entry_id
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def get_entry_by_id(entry_id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT e.*, z.name as zone, c.name as clerk, v.reg_number as vehicle, r.name as route
            FROM daily_entries e
            LEFT JOIN zones z ON e.zone_id = z.id
            LEFT JOIN clerks c ON e.clerk_id = c.id
            LEFT JOIN vehicles v ON e.vehicle_id = v.id
            LEFT JOIN routes r ON e.route_id = r.id
            WHERE e.id=%s
        """
        cursor.execute(query, (entry_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()

def get_all_entries():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
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
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
