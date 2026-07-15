import json
import os

filepath = r"C:\Users\Tanay Kumar\Desktop\2.0\backend\ingestion\data\raw\openfda_metformin.json"
if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("Keys in openfda file:")
    print(list(data.keys()))
    if "openfda" in data:
        print("\nKeys in openfda metadata:")
        print(list(data["openfda"].keys()))
        for k in ["brand_name", "generic_name", "pharm_class_epc", "pharm_class_pe", "route", "substance_name", "unii", "rxcui"]:
            if k in data["openfda"]:
                print(f"  {k}: {data['openfda'][k]}")
else:
    print("File not found.")
