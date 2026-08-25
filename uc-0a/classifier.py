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
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided, so the complaint is classified as Other.",
            "flag": "NEEDS_REVIEW",
        }

    normalized = description.lower()
    urgent_keywords = [
        "injury",
        "child",
        "school",
        "hospital",
        "ambulance",
        "fire",
        "hazard",
        "fell",
        "collapse",
    ]
    severity_matches = [kw for kw in urgent_keywords if kw in normalized]
    priority = "Urgent" if severity_matches else "Standard"

    category_rules = [
        ("Drain Blockage", ["drain blocked", "drain blockage", "blocked drain", "drain is blocked"]),
        ("Streetlight", ["streetlight", "streetlights", "lights out", "lighting", "dark at night", "flickering", "sparking"]),
        ("Pothole", ["pothole", "potholes"]),
        ("Flooding", ["flooded", "flood", "waterlogged", "knee-deep", "standing in water", "bridge approach floods", "inaccessible"]),
        ("Waste", ["garbage", "waste", "trash", "overflowing bins", "dead animal", "bulk waste", "dumped", "removal"]),
        ("Noise", ["noise", "music past midnight", "loud music", "sound past midnight", "late night"]),
        ("Heat Hazard", ["heat hazard", "heatwave", "heat"]),
        ("Road Damage", ["road surface cracked", "sinking", "footpath tiles broken", "broken pavement", "manhole cover missing", "cracked road", "upturned", "road surface", "damaged road"]),
        ("Heritage Damage", ["heritage damage", "heritage building", "heritage structure"]),
    ]

    category = "Other"
    evidence = "description"
    for rule_category, keywords in category_rules:
        for keyword in keywords:
            if keyword in normalized:
                category = rule_category
                evidence = keyword
                break
        if category != "Other":
            break

    if category == "Other":
        # Some heritage complaints may use the word heritage without explicit damage wording.
        if "heritage" in normalized and "streetlight" not in normalized and "lights" not in normalized:
            category = "Heritage Damage"
            evidence = "heritage"

    if category == "Other" and "heritage" in normalized and "streetlight" in normalized:
        category = "Streetlight"
        evidence = "streetlight"

    if category == "Other" and "drain" in normalized and "flood" in normalized:
        category = "Drain Blockage"
        evidence = "drain"

    reason_parts = [f"Description includes '{evidence}'" if evidence != "description" else "Description is not explicit"
                    for evidence in [evidence]]
    if severity_matches:
        reason = f"{reason_parts[0]} and contains '{severity_matches[0]}', so category is {category} and priority is Urgent."
    else:
        reason = f"{reason_parts[0]}, so category is {category}."

    flag = "" if category != "Other" else "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                complaint_id = str(row.get("complaint_id", "")).strip()
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Unable to classify due to invalid row data.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
