"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    severity_keywords = {
        "urgent": ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    }

    categories_map = {
        "Pothole": ["pothole", "hole in road", "road hole"],
        "Flooding": ["flood", "water logging", "waterlogged", "standing water"],
        "Streetlight": ["streetlight", "lamp", "light pole", "dark street", "light not working"],
        "Waste": ["garbage", "trash", "rubbish", "dump", "waste"],
        "Noise": ["noise", "loud", "sound"],
        "Road Damage": ["road damage", "broken road", "crack", "cracks"],
        "Heritage Damage": ["heritage", "monument", "historic", "heritage site"],
        "Heat Hazard": ["heat", "scorch", "hot surface", "heatwave"],
        "Drain Blockage": ["drain", "sewer", "blocked", "blockage", "clog"]
    }

    if not isinstance(row, dict):
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Row is not a valid dictionary format.",
            "flag": "NEEDS_REVIEW"
        }

    description = str(row.get("description") or row.get("complaint") or "").strip()
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Empty or invalid description.",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()
    matched_categories = []
    for cat, keywords in categories_map.items():
        if any(k in text for k in keywords):
            matched_categories.append(cat)

    if not matched_categories:
        category = "Other"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        # ambiguous categories in same text
        category = matched_categories[0]

    # priority logic: urgent if any severity keyword is present
    priority = "Standard"
    if any(word in text for word in severity_keywords["urgent"]):
        priority = "Urgent"
    else:
        if any(term in text for term in ["minor", "small", "low", "resolve later", "not urgent"]):
            priority = "Low"

    # reason includes text evidence and is one sentence
    cited = "".join([f"{word}, " for word in severity_keywords["urgent"] if word in text])
    if cited:
        cited = cited[:-2]
    else:
        for k in categories_map.get(category, []):
            if k in text:
                cited = k
                break

    reason_base = f"Category {category} detected from text" if not cited else f"Category {category} detected from text containing '{cited}'"
    reason = f"{reason_base}." if not reason_base.endswith(".") else reason_base

    flag = ""
    if category == "Other" or len(matched_categories) > 1:
        flag = "NEEDS_REVIEW"

    return {
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
        input_fields = reader.fieldnames or []

        additional_fields = ["category", "priority", "reason", "flag"]
        out_fields = list(input_fields) + [f for f in additional_fields if f not in input_fields]

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()

            for row_num, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                except Exception as exc:
                    result = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error processing row {row_num}: {exc}",
                        "flag": "NEEDS_REVIEW"
                    }

                output_row = dict(row)
                output_row.update(result)
                writer.writerow(output_row)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
