import requests
import os
import sys

BASE_URL = "http://localhost:8000"

payload = {
    "date": "2023-12-19",
    "entries": [
        {
            "date": "2023-12-19",
            "zone": "ZONE 2",
            "clerk": "Sort Test Clerk",
            "vehicle": "KCX 999",
            "route": "Sort Route",
            "fld_wgt": 100.0,
            "fact_wgt": 98.0,
            "scorch_kg": 2.0,
            "quality_pct": 92.0
        }
    ]
}

print("Generating HTML report...")
try:
    # Use the preview endpoint to generate the file
    response = requests.post(f"{BASE_URL}/api/preview/html", json=payload)
    
    if response.status_code == 200:
        content = response.text
        
        checks = {
            "handleSort function": "function handleSort(field)",
            "Clickable Header (Zone)": "onclick=\"handleSort('zone')\"",
            "Sort State": "let currentSort = { field: 'zone', asc: true };",
            "Sort Icon Span": "<span id=\"sort-zone\""
        }
        
        failed = []
        for name, substring in checks.items():
            if substring in content:
                print(f"[PASS] {name} found.")
            else:
                print(f"[FAIL] {name} NOT found.")
                failed.append(name)
        
        if not failed:
            print("\nSUCCESS: All sorting components verified in generated HTML.")
            sys.exit(0)
        else:
            print(f"\nFAILURE: Missing components: {failed}")
            sys.exit(1)
            
    else:
        print(f"Failed to generate report. Status: {response.status_code}")
        sys.exit(1)

except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
