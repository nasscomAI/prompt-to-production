"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns dict with keys: complaint_id, category, priority, reason, flag.
    """
    allowed_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    description = (row.get("description", "") if isinstance(row, dict) else "") or ""
    description_text = str(description).strip()
    lower_desc = description_text.lower()

    if not description_text:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # Category keyword matching rules
    mapping = [
        ("Pothole", ["pothole", "hole"]),
        ("Flooding", ["flood", "flooding", "waterlogged", "water logging", "water in road"]),
        ("Streetlight", ["streetlight", "street light", "lamp", "lamppost", "light out"]),
        ("Waste", ["waste", "garbage", "trash", "dump", "litter"]),
        ("Noise", ["noise", "loud", "horn", "music", "shouting", "sound"]),
        ("Road Damage", ["road damage", "crack", "cracked", "pavement", "road surface"]),
        ("Heritage Damage", ["heritage", "monument", "statue", "historic", "heritage building"]),
        ("Heat Hazard", ["heat", "hot", "heatwave", "sunstroke", "warmth"]),
        ("Drain Blockage", ["drain", "sewage", "gutter", "clog", "blocked drain"])
    ]

    found_categories = []
    matched_words = []
    for category, keywords in mapping:
        for kw in keywords:
            if kw in lower_desc:
                found_categories.append(category)
                matched_words.append(kw)
                break

    if len(found_categories) == 1:
        category = found_categories[0]
        flag = ""
    elif len(found_categories) > 1:
        category = found_categories[0]  # choose first match but flag for ambiguity
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority determination
    priority = "Urgent" if any(sk in lower_desc for sk in severity_keywords) else "Standard"

    # If no severity and some of these minor hints exist, set Low
    low_keywords = ["small", "minor", "not urgent", "low priority", "routine"]
    if priority != "Urgent" and any(kw in lower_desc for kw in low_keywords):
        priority = "Low"

    # Reason generation with cited words
    citation = ", ".join(sorted(set(matched_words))) if matched_words else "no category keyword"
    if priority == "Urgent":
        found_severity = [kw for kw in severity_keywords if kw in lower_desc]
        citation += ", " + ", ".join(found_severity) if found_severity else ""

    reason = f"Classified as {category} with priority {priority} because description mentions {citation}." if citation else f"Classified as {category} with priority {priority}."
    reason = reason.replace("  ", " ").strip()

    if not reason.endswith("."):
        reason += "."

    # Enforce allowed categories exactly
    if category not in allowed_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if flag not in ["", "NEEDS_REVIEW"]:
        flag = ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write results CSV."""
    import os

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    fieldnames_out = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile, \
            open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames_out)
        writer.writeheader()

        for row in reader:
            try:
                if row is None:
                    continue
                if "description" not in row or not str(row.get("description", "")).strip():
                    classified = {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "No description provided.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    classified = classify_complaint(row)
            except Exception as ex:
                classified = {
                    "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error classifying row: {str(ex)}",
                    "flag": "NEEDS_REVIEW"
                }
            writer.writerow(classified)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
