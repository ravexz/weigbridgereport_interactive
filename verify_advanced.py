import sys
import os
import sqlite3
import requests
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from backend.excel_handler import update_excel_report
from backend.database import init_db, save_entry, get_all_entries

def test_advanced_flow():
    init_db()
    
    # 1. Test Metadata Logic
    print("Testing metadata logic...")
    sample_entry = {
        "date": "2023-12-19",
        "zone": "ZONE 2",
        "clerk": "Logic Test",
        "vehicle": "KCX 999",
        "route": "Test Route Metadata",
        "time_out": "08:00",
        "time_in": "17:00",
        "tare_time": "17:30",
        "fld_wgt": 500,
        "fact_wgt": 490,
        "scorch_kg": 5,
        "quality_pct": 95
    }
    save_entry(sample_entry)
    
    entries = get_all_entries()
    vehicles = set(e['vehicle'] for e in entries)
    routes = set(e['route'] for e in entries)
    print(f"Captured Vehicles: {vehicles}")
    print(f"Captured Routes: {routes}")
    
    # 2. Test Excel Mapping with Times
    print("\nTesting Excel mapping with times...")
    report_date = datetime.now().strftime("%Y-%m-%d")
    current_entries = [
        {
            "zone": "ZONE 1 NORAH",
            "clerk": "Time Clerk",
            "vehicle": "TIME-01",
            "route": "Time Route",
            "time_out": "06:30",
            "time_in": "15:45",
            "tare_time": "16:15",
            "fld_wgt": 1000,
            "fact_wgt": 980,
            "scorch_kg": 10,
            "quality_pct": 92
        }
    ]
    
    pdf_path = update_excel_report(current_entries, report_date)
    print(f"Report with timing generated: {pdf_path}")
    
    if os.path.exists(pdf_path):
        print("Verification SUCCESS: PDF file exists.")
    else:
        print("Verification FAILURE: PDF file missing.")

if __name__ == "__main__":
    test_advanced_flow()
