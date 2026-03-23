"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # 1. Determine Category
    categories = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "lights out": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "animal": "Waste",
        "music": "Noise",
        "road": "Road Damage",
        "tiles": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    matched_cats = []
    for kw, cat in categories.items():
        if kw in desc:
            if cat not in matched_cats:
                matched_cats.append(cat)
                
    if len(matched_cats) == 1:
        category = matched_cats[0]
        flag = ""
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    urgent_kw_found = ""
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            urgent_kw_found = kw
            break
            
    # 3. Determine Reason
    if priority == "Urgent":
        reason = f"Classified as Urgent due to presence of severity keyword '{urgent_kw_found}'."
    else:
        reason = f"Classified as {category} based on description."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                res = classify_complaint(row)
                out_row = {
                    "Category": res["category"],
                    "Priority": res["priority"],
                    "Reason": res["reason"],
                    "Flag": res["flag"]
                }
                results.append(out_row)
            except Exception as e:
                # Must not crash on bad rows
                err_row = {
                    "Category": "Other",
                    "Priority": "Low",
                    "Reason": f"Error processing row: {e}",
                    "Flag": "NEEDS_REVIEW"
                }
                results.append(err_row)

    if not results:
        return

    # Write output
    fieldnames = ["Category", "Priority", "Reason", "Flag"]

    if output_path.endswith('.xlsx'):
        try:
            import pandas as pd
            df = pd.DataFrame(results, columns=fieldnames)
            df.to_excel(output_path, index=False)
            print(f"Excel file created successfully: {output_path}")
        except ImportError:
            print("Warning: pandas or openpyxl missing. Falling back to CSV.")
            output_path = output_path.replace('.xlsx', '.csv')
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
    else:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
