import sqlite3
import os

DB_PATH = "reports.db"

def inspect():
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for t in tables:
        print(f"- {t[0]}")
        
    print("\n--- daily_entries Schema ---")
    cursor.execute("PRAGMA table_info(daily_entries)")
    for col in cursor.fetchall():
        print(col)
        
    print("\n--- Zone Lookups ---")
    try:
        cursor.execute("SELECT * FROM zones")
        for z in cursor.fetchall():
            print(z)
    except:
        print("Could not select from zones")

    print("\n--- Sample Entry (JOINED) ---")
    try:
        from backend.database import get_all_entries
        entries = get_all_entries()
        if entries:
            print(entries[0])
        else:
            print("No entries found.")
    except Exception as e:
        print(f"Error fetching entries: {e}")

    conn.close()

if __name__ == "__main__":
    inspect()
