import pandas as pd
import openpyxl

def dump_excel(file_path):
    # Use openpyxl via pandas
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.to_csv(f"{sheet_name}.csv", index=False)
        print(f"Dumped {sheet_name} to {sheet_name}.csv")

if __name__ == "__main__":
    dump_excel("Report.xlsx.xlsm")
