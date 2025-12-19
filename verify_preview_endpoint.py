import requests
import json
import sys

BASE_URL = "http://localhost:8000"

payload = {
    "date": "2023-12-19",
    "entries": [
        {
            "date": "2023-12-19",
            "zone": "ZONE 2",
            "clerk": "Preview Test Clerk",
            "vehicle": "KCX 999",
            "route": "Preview Route",
            "fld_wgt": 100.0,
            "fact_wgt": 98.0,
            "scorch_kg": 2.0,
            "quality_pct": 92.0
        }
    ]
}

def param_test(file_type, expected_content_type):
    print(f"Testing /api/preview/{file_type}...")
    try:
        url = f"{BASE_URL}/api/preview/{file_type}"
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            ctype = response.headers.get("Content-Type", "")
            size = len(response.content)
            print(f"SUCCESS: Status 200, Type: {ctype}, Size: {size} bytes")
            
            if expected_content_type not in ctype:
                print(f"WARNING: Expected Content-Type {expected_content_type}, got {ctype}")
                return False
            
            if size < 100:
                print("ERROR: File too small!")
                return False
                
            return True
        else:
            print(f"FAILURE: Status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

print("--- Starting Preview Endpoint Verification ---")
pdf_ok = param_test("pdf", "application/pdf")
html_ok = param_test("html", "text/html")

if pdf_ok and html_ok:
    print("\nALL PREVIEW TESTS PASSED")
    sys.exit(0)
else:
    print("\nPREVIEW TESTS FAILED")
    sys.exit(1)
