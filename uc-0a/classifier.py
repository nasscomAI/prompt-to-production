"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to agents.md and skills.md rules.
    """
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    severity_keywords = [
        "injury", "injured", "child", "children", "school", "hospital", "hospitalised", "hospitalized",
        "ambulance", "fire", "hazard", "fell", "collapse", "collapsed"
    ]
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = ""
    desc = row.get("description", "")
    complaint_id = row.get("complaint_id", "")
    if not desc or desc.strip() == "":
        category = "Other"
        priority = "Standard"
        flag = "NEEDS_REVIEW"
        reason = "No classifiable description provided"
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }
    desc_lower = desc.lower()
    # Priority assignment
    if any(kw in desc_lower for kw in severity_keywords):
        priority = "Urgent"
    # Category assignment
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "flooded" in desc_lower or "underpass flooded" in desc_lower or "drain blocked" in desc_lower:
        category = "Flooding"
    elif "streetlight" in desc_lower or "light" in desc_lower or "dark" in desc_lower or "wiring theft" in desc_lower:
        category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "bins" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower or "amplifier" in desc_lower or "club music" in desc_lower or "wedding band" in desc_lower:
        category = "Noise"
        if priority == "Standard":
            priority = "Low"
    elif "road" in desc_lower or "surface" in desc_lower or "cracked" in desc_lower or "subsidence" in desc_lower or "collapse" in desc_lower or "sinking" in desc_lower or "manhole" in desc_lower or "bridge" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower or "monument" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "burn" in desc_lower or "bubbling" in desc_lower:
        category = "Heat Hazard"
    elif "drain" in desc_lower or "drainage" in desc_lower or "blocked" in desc_lower or "mosquito" in desc_lower:
        category = "Drain Blockage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
    # Reason field
    reason = f"Classified as {category} because description contains: '{desc.strip()[:80]}'"
    # Heritage enforcement
    if category == "Heritage Damage" and not (
        "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower or "monument" in desc_lower):
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Heritage category not justified: '{desc.strip()[:80]}'"
    # Multi-category enforcement
    if category == "Other":
        flag = "NEEDS_REVIEW"
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV. Robust to malformed rows.
    """
    import sys
    results = []
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    cid = row.get("complaint_id", "UNKNOWN")
                    print(f"Warning: Failed to classify complaint_id {cid}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error: Could not read input file {input_path}: {e}", file=sys.stderr)
        return
    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
    except Exception as e:
        print(f"Error: Could not write output file {output_path}: {e}", file=sys.stderr)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
