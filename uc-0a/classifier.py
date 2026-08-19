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
    desc = row.get("description", "").strip()
    if not desc:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Check severity keywords for urgent priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    desc_lower = desc.lower()
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    
    # Priority determination
    if is_urgent:
        priority = "Urgent"
    else:
        try:
            days = int(row.get("days_open", 0))
        except ValueError:
            days = 0
        priority = "Standard" if days > 5 else "Low"

    # Category matching rules
    matched_categories = []
    
    if "pothole" in desc_lower or "crater" in desc_lower:
        matched_categories.append("Pothole")
    if "flood" in desc_lower or "waterlog" in desc_lower or "water log" in desc_lower or "waterlogging" in desc_lower:
        matched_categories.append("Flooding")
    if "streetlight" in desc_lower or "light out" in desc_lower or "lights out" in desc_lower or "flicker" in desc_lower or "dark at night" in desc_lower or "unlit" in desc_lower or "darkness" in desc_lower:
        matched_categories.append("Streetlight")
    if "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "dump" in desc_lower or "dead animal" in desc_lower:
        matched_categories.append("Waste")
    if "music" in desc_lower or "noise" in desc_lower or "loudspeaker" in desc_lower or "amplifier" in desc_lower:
        matched_categories.append("Noise")
    if "footpath" in desc_lower or "manhole" in desc_lower or "surface cracked" in desc_lower or "road surface" in desc_lower or "buckled" in desc_lower or "subsided" in desc_lower or "subsidence" in desc_lower or "collapsed" in desc_lower or "paving" in desc_lower:
        matched_categories.append("Road Damage")
    if "heritage" in desc_lower or "historic" in desc_lower or "monument" in desc_lower or "ancient" in desc_lower:
        matched_categories.append("Heritage Damage")
    if "heat" in desc_lower or "sun" in desc_lower or "hot" in desc_lower or "shade" in desc_lower or "shelter" in desc_lower or "melting" in desc_lower or "temperature" in desc_lower:
        matched_categories.append("Heat Hazard")
    if "drain" in desc_lower or "sewage" in desc_lower or "gutter" in desc_lower or "blockage" in desc_lower or "clog" in desc_lower:
        matched_categories.append("Drain Blockage")

    # Resolve category and ambiguity flag
    flag = ""
    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = matched_categories[0]

    # Generate reason: one sentence citing specific words from description
    first_sentence = desc.split(".")[0].split(";")[0].strip()
    if not first_sentence.endswith("."):
        first_sentence += "."
    
    reason = f"The complaint cites '{first_sentence}' as the core issue."
    
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
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Handle error per row and continue
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
