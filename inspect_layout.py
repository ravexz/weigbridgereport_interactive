import win32com.client as win32
import os

def inspect_excel_layout(file_path):
    abs_path = os.path.abspath(file_path)
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False
    try:
        wb = excel.Workbooks.Open(abs_path)
        sheet = wb.Worksheets("Report")
        
        print(f"Sheet Name: {sheet.Name}")
        print(f"Page Orientation: {'Portrait' if sheet.PageSetup.Orientation == 1 else 'Landscape'}")
        print(f"FitToPagesWide: {sheet.PageSetup.FitToPagesWide}")
        print(f"FitToPagesTall: {sheet.PageSetup.FitToPagesTall}")
        
        chart_objects = sheet.ChartObjects()
        print(f"\nNumber of Charts: {chart_objects.Count}")
        for i in range(1, chart_objects.Count + 1):
            chart = chart_objects.Item(i)
            print(f"Chart {i}: Name={chart.Name}, Top={chart.Top}, Left={chart.Left}, Height={chart.Height}, Width={chart.Width}")
            
        wb.Close(False)
    finally:
        excel.Quit()

if __name__ == "__main__":
    inspect_excel_layout("Report.xlsx.xlsm")
