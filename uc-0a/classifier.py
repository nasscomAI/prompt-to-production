import argparse
import csv
import glob
import os
import re

# More expandable, future-proof taxonomy logic
CATEGORY_RULES = {
    "Pothole": r"\b(pothole|crater|pit|hole)\b",
    "Flooding": r"\b(flood|water|submerge|overflow|monsoon)\b",
    "Streetlight": r"\b(light|lamp|dark|bulb)\b",
    "Waste": r"\b(waste|garbage|trash|dump|rubbish|litter)\b",
    "Noise": r"\b(noise|loud|music|speaker|sound|decibel)\b",
    "Road Damage": r"\b(road|crack|cave|surface|asphalt|tar)\b",
    "Heritage Damage": r"\b(heritage|monument|statue|fort|historic)\b",
    "Heat Hazard": r"\b(heat|sun|temperature|hot|wave)\b",
    "Drain Blockage": r"\b(drain|clog|sewer|block|choke|sewage)\b"
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse", "risk"]
HIGH_LEVERAGE_REPORTERS = ["councillor referral", "vip", "mayor"]

def classify_complaint(row, location_counts):
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Check severity
    priority = "Standard"
    urgent_reasons = []

    # 1. Check description for severity keywords
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            urgent_reasons.append(f"severity keyword '{kw}'")
            break # Just need one

    # 2. Check days_open
    try:
        days_open = int(row.get("days_open", 0))
    except ValueError:
        days_open = 0
        
    if days_open >= 10:
        priority = "Urgent"
        urgent_reasons.append(f"open for {days_open} days")

    # 3. Check repeated locations
    location = row.get("location", "").strip()
    if location and location_counts.get(location, 0) > 1:
        priority = "Urgent"
        urgent_reasons.append(f"repeated location complaints ({location_counts[location]} total)")

    # 4. Check reported_by
    reporter = row.get("reported_by", "").lower()
    if any(hlr in reporter for hlr in HIGH_LEVERAGE_REPORTERS):
        priority = "Urgent"
        urgent_reasons.append(f"reported by VIP ({row.get('reported_by', '')})")

    # Check categories using regex patterns
    matched_categories = []
    for cat, pattern in CATEGORY_RULES.items():
        if re.search(pattern, desc_lower):
            matched_categories.append(cat)

    matched_categories = list(set(matched_categories))

    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        first_word = description.split()[0] if description.split() else "empty text"
        reason = f"Could not determine category from words like '{first_word}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Complaint contains overlapping topics like '{matched_categories[0]}' and '{matched_categories[1]}'."
    else:
        category = matched_categories[0]
        reason = f"The description mentions words related to '{category}'."

    if priority == "Urgent":
        reason += " " + (" Marked Urgent due to: " + " and ".join(urgent_reasons) + ".")
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }

def batch_classify(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        if fields is None:
            return
        rows = list(reader)

    # Pre-calculate metadata (e.g. repeated locations)
    location_counts = {}
    for r in rows:
        loc = r.get("location", "").strip()
        if loc:
            location_counts[loc] = location_counts.get(loc, 0) + 1

    # Ensure output columns
    out_fields = list(fields)
    for expected_col in ["category", "priority_flag", "reason", "flag"]:
        if expected_col not in out_fields and expected_col != "priority_flag":
            out_fields.append(expected_col)
    if "priority" not in out_fields:
        out_fields.append("priority")

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        
        for row in rows:
            res = classify_complaint(row, location_counts)
            row["category"] = res["category"]
            row["priority"] = res["priority"]
            row["reason"] = res["reason"]
            row["flag"] = res["flag"]
            writer.writerow(row)
            
    print(f"✅ Processed {len(rows)} rows from {input_csv} -> {output_csv}")

def process_all_cities():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data", "city-test-files")
    search_path = os.path.join(data_dir, "test_*.csv")
    csv_files = glob.glob(search_path)
    if not csv_files:
        print(f"No files found matching {search_path}")
        return
        
    for f in csv_files:
        basename = os.path.basename(f)
        city = basename.replace("test_", "").replace(".csv", "")
        out_file = os.path.join(base_dir, f"results_{city}.csv")
        batch_classify(f, out_file)

def main():
    parser = argparse.ArgumentParser(description="Complaint Classifier")
    parser.add_argument("--input", help="Input CSV file path")
    parser.add_argument("--output", help="Output CSV file path")
    args = parser.parse_args()
    
    if args.input and args.output:
        batch_classify(args.input, args.output)
    else:
        print("No specific --input/--output provided. Processing all city test files...")
        process_all_cities()

if __name__ == "__main__":
    main()
