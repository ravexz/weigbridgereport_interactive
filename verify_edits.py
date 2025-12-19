import sqlite3
import requests
import time
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api"

def verify_edits():
    # 1. Create a fresh record
    print("Creating a fresh record...")
    res = requests.post(f"{API_URL}/submit", json={
        "date": "2025-12-19",
        "entries": [{
            "date": "2025-12-19",
            "zone": "ZONE 1 NORAH",
            "clerk": "Edit Tester",
            "vehicle": "EDIT-01",
            "route": "Edit Route",
            "fld_wgt": 100,
            "fact_wgt": 100,
            "scorch_kg": 0,
            "quality_pct": 100
        }]
    })
    print(f"Submit result: {res.json()}")
    
    # Get the ID of the new record
    entries = requests.get(f"{API_URL}/entries").json()
    new_entry = [e for e in entries if e['vehicle'] == "EDIT-01"][0]
    entry_id = new_entry['id']
    print(f"New Entry ID: {entry_id}")

    # 2. Update the record immediately (should pass)
    print("\nUpdating fresh record (within 48h)...")
    updated_data = new_entry.copy()
    updated_data['clerk'] = "Updated Tester"
    res = requests.put(f"{API_URL}/entries/{entry_id}", json=updated_data)
    print(f"Update result: {res.status_code} {res.json()}")

    # 3. Simulate an old record by direct database manipulation
    print("\nSimulating an old record (>48h)...")
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()
    old_time = (datetime.now() - timedelta(hours=50)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE daily_entries SET created_at = ? WHERE id = ?", (old_time, entry_id))
    conn.commit()
    conn.close()

    # 4. Try updating the old record (should fail)
    print("Updating old record (outside 48h)...")
    res = requests.put(f"{API_URL}/entries/{entry_id}", json=updated_data)
    print(f"Old record update result: {res.status_code} {res.json()}")
    if res.status_code == 403:
        print("Verification SUCCESS: Edit blocked for old record.")
    else:
        print("Verification FAILURE: Edit NOT blocked for old record.")

if __name__ == "__main__":
    verify_edits()
    print("\nCheck uvicorn logs for email delivery simulation to dmronoh.12@gmail.com")
