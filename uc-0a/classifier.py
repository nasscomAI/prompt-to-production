import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row):
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    category = "Other"
    reason_keywords = []
    
    if "pothole" in desc:
        category = "Pothole"
        reason_keywords.append("pothole")
    elif "flood" in desc or "underpass" in desc or "standing in water" in desc:
        category = "Flooding"
        reason_keywords.append("flooding/waterlogging")
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        reason_keywords.append("drain/manhole issue")
    elif "heritage" in desc:
        category = "Heritage Damage"
        reason_keywords.append("heritage site concern")
    elif "streetlight" in desc or "lights out" in desc or "dark at night" in desc:
        category = "Streetlight"
        reason_keywords.append("streetlight/lighting issue")
    elif "garbage" in desc or "waste" in desc or "dead animal" in desc:
        category = "Waste"
        reason_keywords.append("waste/garbage accumulation")
    elif "music" in desc or "noise" in desc:
        category = "Noise"
        reason_keywords.append("noise disturbance")
    elif "cracked" in desc or "sinking" in desc or "footpath" in desc or "tiles broken" in desc or "road surface" in desc:
        category = "Road Damage"
        reason_keywords.append("road/footpath surface damage")
    elif "heat" in desc or "sunstroke" in desc:
        category = "Heat Hazard"
        reason_keywords.append("heat condition")

    # Double check allowed category
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    # 2. Determine Priority
    priority = "Standard"
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc)]
    if matched_severity:
        priority = "Urgent"
    elif int(row.get("days_open", 0)) > 15:
        priority = "Urgent"

    # 3. Determine Reason
    if matched_severity:
        reason = f"Classified as {category} with Urgent priority due to severity indicators ('{', '.join(matched_severity)}') in description."
    else:
        reason = f"Classified as {category} with {priority} priority based on report of {', '.join(reason_keywords) if reason_keywords else 'civic issue'}."

    # 4. Determine Flag
    flag = ""
    if category == "Other" or ("pothole" in desc and "drain" in desc):
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_file, output_file):
    with open(input_file, mode="r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames)
        
        # Append classification output columns
        for col in ["category", "priority", "reason", "flag"]:
            if col not in fieldnames:
                fieldnames.append(col)
                
        rows = []
        for row in reader:
            res = classify_complaint(row)
            row["category"] = res["category"]
            row["priority"] = res["priority"]
            row["reason"] = res["reason"]
            row["flag"] = res["flag"]
            rows.append(row)

    with open(output_file, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully classified {len(rows)} records into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
