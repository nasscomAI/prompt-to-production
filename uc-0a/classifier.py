"""
UC-0A — Complaint Classifier
Implementation based on RICE framework.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def classify_complaint(row: dict) -> dict:
    """
    Classifies a single citizen complaint description into an exact predefined category and priority, 
    providing a single-sentence justification and flagging ambiguity.
    """
    desc = row.get("description", "").lower()
    
    # Priority classification
    found_severities = [kw for kw in SEVERITY_KEYWORDS if kw in desc]
    priority = "Urgent" if found_severities else "Standard"
    
    # Category classification based on string matching heuristics
    matched_cats = set()
    if "pothole" in desc: matched_cats.add("Pothole")
    if "flood" in desc or "standing in water" in desc: matched_cats.add("Flooding")
    if "streetlight" in desc or "lights out" in desc or "dark at night" in desc: matched_cats.add("Streetlight")
    if "waste" in desc or "garbage" in desc or "dead animal" in desc: matched_cats.add("Waste")
    if "music" in desc or "noise" in desc: matched_cats.add("Noise")
    if "road surface cracked" in desc or "footpath tiles broken" in desc: matched_cats.add("Road Damage")
    if "heritage" in desc: matched_cats.add("Heritage Damage")
    if "heat" in desc: matched_cats.add("Heat Hazard")
    if "drain block" in desc or "drain" in desc: matched_cats.add("Drain Blockage")
    
    category = "Other"
    flag = ""
    cited_match = ""
    
    # Decision logic
    if len(matched_cats) == 1:
        category, = matched_cats
        if "pothole" in desc: cited_match = "pothole"
        elif "flood" in desc: cited_match = "flood"
        elif "lights" in desc: cited_match = "lights"
        elif "streetlight" in desc: cited_match = "streetlight"
        elif "garbage" in desc: cited_match = "garbage"
        elif "waste" in desc: cited_match = "waste"
        elif "animal" in desc: cited_match = "animal"
        elif "music" in desc: cited_match = "music"
        elif "drain" in desc: cited_match = "drain"
        elif "heritage" in desc: cited_match = "heritage"
        elif "road" in desc: cited_match = "road"
        elif "footpath" in desc: cited_match = "footpath"
        else: cited_match = category.lower()
    elif len(matched_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cited_match = "multiple issues"
    else:
        if "manhole" in desc:
            category = "Other"
            flag = "NEEDS_REVIEW"
            cited_match = "manhole"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            cited_match = "unclear descriptions"

    # Construct the reason sentence dynamically
    if category != "Other":
        reason_cat = f"Categorized as {category} based on the word '{cited_match}'"
    else:
        reason_cat = f"Categorized as Other and flagged for review because the description contains {cited_match}"

    if priority == "Urgent":
        reason = f"{reason_cat} and flagged Urgent due to the severity keyword '{found_severities[0]}'."
    else:
        reason = f"{reason_cat} with Standard priority."

    # Construct output record
    result = row.copy()
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag
    
    return result

def batch_classify(input_path: str, output_path: str):
    """
    Reads an input CSV of citizen complaints, iteratively applies the classify_complaint
    skill to each row, and writes all results to an output CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_path}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
        
    if not rows:
        print("Error: Input file is empty.")
        sys.exit(1)

    classified_rows = []
    for row in rows:
        try:
            result = classify_complaint(row)
            classified_rows.append(result)
        except Exception as e:
            # error handling per skills.md: flag row invalid rather than halting batch
            print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
            error_row = row.copy()
            error_row["category"] = "Other"
            error_row["priority"] = "Low"
            error_row["reason"] = f"Processing error: {e}"
            error_row["flag"] = "NEEDS_REVIEW"
            classified_rows.append(error_row)

    try:
        if classified_rows:
            fieldnames = list(classified_rows[0].keys())
            with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(classified_rows)
    except Exception as e:
        print(f"Error writing output file '{output_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified {args.input} and wrote results to {args.output}")
