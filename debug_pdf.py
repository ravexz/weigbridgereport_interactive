import win32com.client as win32
import os
import sqlite3
import time
from backend.excel_handler import update_excel_report

def debug_pdf_flow():
    # 1. Get some real data from DB
    conn = sqlite3.connect("reports.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_entries LIMIT 5")
    entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not entries:
        print("No entries found in DB for debugging.")
        return

    report_date = entries[0]['date']
    print(f"Using date: {report_date}")
    
    # 2. Run the update function
    xl_path = update_excel_report(entries, report_date)
    print(f"Excel Path: {xl_path}")
    
    pdf_path = xl_path.replace(".xlsm", ".pdf").replace(".xlsx", ".pdf")
    
    # 3. Inspect via COM
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(os.path.abspath(xl_path))
        sheet = wb.Worksheets("Report")
        
        print("\n--- COM INSPECTION ---")
        print(f"Cell F4 (Date): {sheet.Range('F4').Value}")
        print(f"Cell D6 (Zone): {sheet.Range('D6').Value}")
        print(f"Cell E6 (Clerk): {sheet.Range('E6').Value}")
        
        # Check if row 6 is hidden
        print(f"Row 6 Hidden: {sheet.Rows('6:6').Hidden}")
        print(f"Row 7 Hidden: {sheet.Rows('7:7').Hidden}")
        
        # Check used range
        print(f"Used Range: {sheet.UsedRange.Address}")
        
        # Export again and check file size
        wb.ExportAsFixedFormat(0, os.path.abspath(pdf_path))
        print(f"PDF Generated at: {pdf_path}")
        print(f"PDF Size: {os.path.getsize(pdf_path)} bytes")
        
        wb.Close(False)
    finally:
        excel.Quit()

if __name__ == "__main__":
    debug_pdf_flow()
