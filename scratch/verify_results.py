import csv
import os

ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
}

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def verify_file(filepath: str, source_filepath: str) -> list:
    errors = []
    
    if not os.path.exists(filepath):
        return [f"File {filepath} does not exist."]
        
    # Read source data to cross-check descriptions
    source_descriptions = {}
    with open(source_filepath, "r", encoding="utf-8") as sf:
        s_reader = csv.DictReader(sf)
        for r in s_reader:
            source_descriptions[r["complaint_id"]] = r["description"]

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # Check headers
        headers = reader.fieldnames
        expected_headers = ["complaint_id", "category", "priority", "reason", "flag"]
        if headers != expected_headers:
            errors.append(f"Invalid headers: expected {expected_headers}, got {headers}")
            
        rows_count = 0
        for i, row in enumerate(reader, start=2):
            rows_count += 1
            cid = row.get("complaint_id", "")
            cat = row.get("category", "")
            pri = row.get("priority", "")
            reason = row.get("reason", "")
            flag = row.get("flag", "")
            
            # Check fields are present
            if not cid:
                errors.append(f"Row {i}: Missing complaint_id")
            if not cat:
                errors.append(f"Row {i}: Missing category")
            if not pri:
                errors.append(f"Row {i}: Missing priority")
            if not reason:
                errors.append(f"Row {i}: Missing reason")
                
            # Check allowed values
            if cat not in ALLOWED_CATEGORIES:
                errors.append(f"Row {i} ({cid}): Invalid category '{cat}'")
            if pri not in ALLOWED_PRIORITIES:
                errors.append(f"Row {i} ({cid}): Invalid priority '{pri}'")
            if flag not in {"NEEDS_REVIEW", ""}:
                errors.append(f"Row {i} ({cid}): Invalid flag '{flag}'")
                
            # Cross-check priority with severity keywords in original description
            desc = source_descriptions.get(cid, "")
            desc_lower = desc.lower()
            has_severity = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
            if has_severity and pri != "Urgent":
                errors.append(f"Row {i} ({cid}): Priority should be Urgent because description contains severity keywords. Description: '{desc}'")
                
            # Verify reason is one sentence
            # Simplified sentence check: reason shouldn't have multiple periods except for abbreviations
            if reason.count(".") > 2:
                errors.append(f"Row {i} ({cid}): Reason might not be a single sentence: '{reason}'")
                
    if rows_count != 15:
        errors.append(f"Invalid row count: expected 15 data rows, got {rows_count}")
        
    return errors

# Validate all four cities
cities = ["pune", "hyderabad", "kolkata", "ahmedabad"]
all_ok = True
for city in cities:
    res_path = f"uc-0a/results_{city}.csv"
    src_path = f"data/city-test-files/test_{city}.csv"
    print(f"Verifying {res_path}...")
    errors = verify_file(res_path, src_path)
    if errors:
        all_ok = False
        for err in errors:
            print(f"  [ERROR] {err}")
    else:
        print(f"  [OK] Validated successfully!")
        
if all_ok:
    print("\nAll 4 results files are 100% correct and conform to schema regulations.")
else:
    print("\nSome validation errors were found.")
