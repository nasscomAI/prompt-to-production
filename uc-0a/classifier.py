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
    # Category assignment — ordered from most specific to least specific
    if "pothole" in desc_lower:
        category = "Pothole"
    elif any(kw in desc_lower for kw in ["melting", "temperature", "heat hazard", "bubbling", "burns on contact", "full sun", "dangerous temp"]):
        category = "Heat Hazard"
    elif any(kw in desc_lower for kw in ["drain blocked", "drain blockage", "stormwater drain", "main drain", "drain completely", "mosquito", "drainage"]):
        category = "Drain Blockage"
    elif any(kw in desc_lower for kw in ["flood", "flooded", "flooding", "waterlogged", "standing water", "knee-deep", "submerged"]):
        category = "Flooding"
    elif any(kw in desc_lower for kw in ["streetlight", "street light", "wiring theft"]) or (("light" in desc_lower or "dark" in desc_lower or "unlit" in desc_lower) and "streetlight" in desc_lower):
        category = "Streetlight"
    elif "unlit" in desc_lower or ("light" in desc_lower and ("out" in desc_lower or "flickering" in desc_lower or "sparking" in desc_lower or "darkness" in desc_lower)):
        category = "Streetlight"
    elif any(kw in desc_lower for kw in ["waste", "garbage", "bins", "dead animal", "dumped", "overflowing"]):
        category = "Waste"
    elif any(kw in desc_lower for kw in ["music", "noise", "amplifier", "drilling", "trucks idling", "idling with engines", "band playing", "wedding band", "club music"]):
        category = "Noise"
        if priority == "Standard":
            priority = "Low"
    elif any(kw in desc_lower for kw in ["heritage", "historic", "ancient", "monument", "cobblestone", "heritage zone", "heritage lamp"]):
        category = "Heritage Damage"
    elif any(kw in desc_lower for kw in ["pothole", "road collapsed", "road collapse", "crater", "road surface", "subsidence", "sinking", "manhole", "footpath", "tarmac", "road damage", "road subsid", "buckled", "cracked"]):
        category = "Road Damage"
    elif any(kw in desc_lower for kw in ["surface", "road", "bridge", "lane"]):
        category = "Road Damage"
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
    print(f"Done. Results written to {output_path}")
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
