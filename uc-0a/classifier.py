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
    severity_keywords = {
        "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
    }

    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage",
        "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]

    category_map = {
        "Pothole": ["pothole", "tyre damage", "manhole cover missing", "hole in road"],
        "Flooding": ["flood", "flooded", "waterlogged", "knee-deep", "inund", "rain"],
        "Streetlight": ["streetlight", "lights out", "dark at night", "lamp", "lighting"],
        "Waste": ["garbage", "bins", "waste", "trash", "overflowing", "dumped", "dead animal"],
        "Noise": ["music", "noise", "loud", "party", "early morning"],
        "Road Damage": ["crack", "road surface", "sinking", "broken", "depression"],
        "Heritage Damage": ["heritage", "heritage street", "old city", "historic"],
        "Heat Hazard": ["heat", "heat wave", "hot", "scorching"],
        "Drain Blockage": ["drain", "blocked", "drain blocked", "sewer"]
    }

    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()
    text = description.lower()

    matched_categories = []
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in text:
                matched_categories.append(cat)
                break

    if len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if category not in allowed_categories:
        category = "Other"

    priority = "Standard"
    if any(word in text for word in severity_keywords):
        priority = "Urgent"
    elif "low" in text or "not urgent" in text or "normal" in text:
        priority = "Low"

    # Ensure severity keyword rule is enforced
    if priority != "Urgent" and any(word in text for word in severity_keywords):
        priority = "Urgent"

    # Build reason that cites description keywords
    cited_words = []
    for kw in ["pothole", "flood", "streetlight", "garbage", "noise", "road", "heritage", "heat", "drain", "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]:
        if kw in text:
            cited_words.append(kw)
    cited_words = list(dict.fromkeys(cited_words))

    if cited_words:
        cited_part = ", ".join(cited_words[:3])
        reason = f"Based on description mentioning {cited_part}, classified as {category}."
    elif description:
        reason = f"Description provided with no keyword match; defaulting to {category}."
    else:
        reason = "No description provided; categorized as Other with review needed."

    # Ensure reason is one sentence
    if not reason.strip().endswith('.'):
        reason = reason.strip() + '.'

    # Flag ambiguous situations
    if flag != "NEEDS_REVIEW" and len(matched_categories) != 1:
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
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        output_fields = ["complaint_id", "category", "priority", "reason", "flag"]

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                try:
                    classified = classify_complaint(row)
                    if not classified.get("reason"):
                        classified["reason"] = "No reason generated; needs review."
                    if classified.get("flag") not in ["NEEDS_REVIEW", ""]:
                        classified["flag"] = ""
                except Exception as e:
                    classified = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    }
                writer.writerow({k: classified.get(k, "") for k in output_fields})



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
