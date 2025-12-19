import os
import sys
from backend.main import save_html_report_to_file
from backend.excel_handler import update_excel_report
from backend.database import get_entries_by_date, init_db, save_entry

# Mock data needed?
def test_workflow():
    init_db()
    
    # 1. Create dummy data if needed
    date = "2023-12-19"
    entries = get_entries_by_date(date)
    if not entries:
        print("No entries found, creating dummy entry...")
        save_entry({
            "date": date,
            "zone": "TEST ZONE",
            "clerk": "DEBUGGER",
            "vehicle": "KAA 123",
            "route": "R1",
            "time_out": "06:00",
            "time_in": "10:00",
            "tare_time": "0.5",
            "fld_wgt": 100.0,
            "fact_wgt": 95.0,
            "scorch_kg": 0.0,
            "quality_pct": 85.0
        })
        entries = get_entries_by_date(date)
    
    print(f"Found {len(entries)} entries for {date}")
    
    # 2. Test Excel/PDF Gen
    print("\n--- Testing Excel/PDF Generation ---")
    try:
        pdf_path = update_excel_report(entries, date)
        print(f"Excel/PDF Generation Success: {pdf_path}")
        if not os.path.exists(pdf_path):
            print("ERROR: File returned but does not exist!")
    except Exception as e:
        print(f"Excel Generation Failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Test HTML Gen
    print("\n--- Testing HTML Generation ---")
    try:
        entries_dicts = [dict(e) for e in entries] # Convert Row to dict
        html_path = save_html_report_to_file(date, entries_dicts)
        print(f"HTML Generation Success: {html_path}")
        if not os.path.exists(html_path):
             print("ERROR: File returned but does not exist!")
    except Exception as e:
        print(f"HTML Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow()
