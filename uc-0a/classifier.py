import argparse
import csv
import sys

# Categorization Schema
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Priority Severity triggers
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", 
    "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on instructions mapped from agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine Category & Flag
    category = "Other"
    flag = ""
    
    # Heuristic mapping
    if "pothole" in desc:
        category = "Pothole"
    elif "drain block" in desc or "drain blocked" in desc or "drain" in desc and "block" in desc:
        category = "Drain Blockage"
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
    elif "streetlight" in desc or "lights out" in desc or "dark" in desc:
        category = "Streetlight"
    elif "waste" in desc or "garbage" in desc or "animal" in desc or "smell" in desc or "dump" in desc:
        category = "Waste"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
    elif "road surface" in desc or "crack" in desc or "manhole" in desc or "footpath" in desc:
        category = "Road Damage"
    elif "heritage" in desc:
        category = "Heritage Damage"
    elif "heat" in desc:
        category = "Heat Hazard"
    else:
        # Ambiguous categories
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Enforce allowed list rigidly
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    priority = "Standard"
    cited_keyword = next((kw for kw in SEVERITY_KEYWORDS if kw in desc), None)
    
    if cited_keyword:
        priority = "Urgent"

    # 3. Formulate Reason
    # Extract specific consecutive words to 'cite specific words from the description'
    words = desc.split()
    snippet = " ".join(words[:4]) if len(words) >= 4 else desc

    if priority == "Urgent":
        reason = f"Classified as '{category}' and Urgent priority because the complaint states '{snippet}' and includes the severity trigger '{cited_keyword}'."
    else:
        reason = f"Classified as '{category}' with Standard priority based on the complaint stating '{snippet}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV, maps each row to classify_complaint, and writes results safely.
    Follows skills.md requirements to flag nulls, skip bad rows without crashing.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row_num, row in enumerate(reader, start=1):
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    # Skills.md enforcement: Do not crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_ERR_{row_num}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Failed to parse description.",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        sys.exit(1)
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
