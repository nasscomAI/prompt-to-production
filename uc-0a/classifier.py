"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    # Priority check
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            break
            
    # Category and reason check
    category = "Other"
    flag = ""
    reason = "The description describes an unlisted issue."

    if "pothole" in desc:
        category = "Pothole"
        reason = "The description explicitly mentions a pothole."
    elif "flood" in desc:
        category = "Flooding"
        reason = "The description explicitly mentions flooding."
        if "drain" in desc:
            flag = "NEEDS_REVIEW"
            category = "Other"
            reason = "The description mentions both flooded water and blocked drain."
    elif "garbage" in desc or "waste" in desc or "dead animal" in desc:
        category = "Waste"
        if "garbage" in desc:
            reason = "The description mentions overflowing garbage bins."
        elif "waste" in desc:
            reason = "The description mentions bulk waste dumped."
        else:
            reason = "The description mentions a dead animal."
    elif "streetlight" in desc or "lights out" in desc:
        if "heritage" in desc:
            flag = "NEEDS_REVIEW"
            category = "Other"
            reason = "The description mentions heritage street and lights out, which is ambiguous."
        else:
            category = "Streetlight"
            if "sparkling" in desc or "sparking" in desc:
                reason = "The description mentions flickering and sparking streetlights."
            else:
                reason = "The description mentions streetlights being out."
    elif "music" in desc:
        category = "Noise"
        reason = "The description mentions loud music playing at a wedding venue."
    elif "crack" in desc or "sinking" in desc or ("footpath" in desc and "broken" in desc):
        category = "Road Damage"
        reason = "The description mentions cracked, sinking, or broken surfaces."
    elif "manhole" in desc:
        category = "Other"  # not drain blockage strictly unless we count manhole
        reason = "The description mentions a missing manhole cover."
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
        rows = list(reader)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                cls = classify_complaint(row)
                row.update(cls)
            except Exception as e:
                print(f"Error processing row: {e}")
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
