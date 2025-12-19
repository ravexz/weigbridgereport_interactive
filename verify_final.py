import sys
import os
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from backend.excel_handler import update_excel_report
from backend.database import init_db, save_entry

def test_full_flow():
    init_db()
    
    # Add some historical data if db is empty
    sample_data = [
        {"date": "2023-12-10", "zone": "ZONE 1 NORAH", "clerk": "Test 1", "vehicle": "V1", "route": "R1", "fld_wgt": 100, "fact_wgt": 95, "scorch_kg": 1, "quality_pct": 98},
        {"date": "2023-12-11", "zone": "ZONE 2", "clerk": "Test 2", "vehicle": "V2", "route": "R2", "fld_wgt": 200, "fact_wgt": 190, "scorch_kg": 2, "quality_pct": 95},
        {"date": "2023-12-12", "zone": "ZONE 3 DENNIS", "clerk": "Test 3", "vehicle": "V3", "route": "R3", "fld_wgt": 300, "fact_wgt": 285, "scorch_kg": 3, "quality_pct": 97},
        {"date": "2023-12-13", "zone": "ZONE 4 WESTONE", "clerk": "Test 4", "vehicle": "V4", "route": "R4", "fld_wgt": 400, "fact_wgt": 380, "scorch_kg": 4, "quality_pct": 96},
    ]
    
    for entry in sample_data:
        save_entry(entry)
    
    # Current entries to group
    current_entries = [
        {"zone": "ZONE 1 NORAH", "clerk": "Clerk A", "vehicle": "Truck 1", "route": "Route Alpha", "fld_wgt": 120, "fact_wgt": 118, "scorch_kg": 0.5, "quality_pct": 99},
        {"zone": "ZONE 1 NORAH", "clerk": "Clerk B", "vehicle": "Truck 2", "route": "Route Beta", "fld_wgt": 110, "fact_wgt": 105, "scorch_kg": 0.3, "quality_pct": 98},
        {"zone": "ZONE 2", "clerk": "Clerk C", "vehicle": "Van 1", "route": "Route Gamma", "fld_wgt": 150, "fact_wgt": 145, "scorch_kg": 1.0, "quality_pct": 94},
        {"zone": "ZONE 3 DENNIS", "clerk": "Clerk D", "vehicle": "Truck 3", "route": "Route Delta", "fld_wgt": 200, "fact_wgt": 195, "scorch_kg": 0.8, "quality_pct": 97},
    ]
    
    report_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Generating report for {report_date}...")
    pdf_path = update_excel_report(current_entries, report_date)
    print(f"Report generated: {pdf_path}")

if __name__ == "__main__":
    test_full_flow()
