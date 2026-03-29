"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns a dict containing category, priority, reason, and flag.
    """
    if not isinstance(row, dict):
        raise ValueError("row must be a dict")

    description = (row.get("description") or row.get("complaint") or "").strip()
    if not description:
        raise ValueError("description is required for classification")

    text = description.lower()

    category_keywords = {
        "Pothole": ["pothole", "pot hole"],
        "Flooding": ["flood", "water logging", "waterlogging", "standing water"],
        "Streetlight": ["streetlight", "street light", "lamp post", "light post"],
        "Waste": ["trash", "garbage", "waste", "dump", "dumping"],
        "Noise": ["noise", "loud", "honking", "music", "construction noise"],
        "Road Damage": ["road damage", "broken road", "road crack", "road sinking"],
        "Heritage Damage": ["heritage", "monument", "historical", "antique"],
        "Heat Hazard": ["heat", "hot", "temperature", "sunstroke"],
        "Drain Blockage": ["drain", "sewer", "gutter", "blocked drain", "clogged drain"],
    }

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    found_categories = []
    for cat, keys in category_keywords.items():
        for keyword in keys:
            if keyword in text:
                found_categories.append(cat)
                break

    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        # multiple matches indicate ambiguity, choose first but flag review
        category = found_categories[0]
    else:
        category = "Other"

    priority = "Standard"
    triggered_severity = []
    for kw in severity_keywords:
        if kw in text:
            priority = "Urgent"
            triggered_severity.append(kw)

    flag = ""
    if category == "Other" or len(found_categories) > 1:
        flag = "NEEDS_REVIEW"

    reason_parts = []
    if found_categories:
        reason_parts.append(f"category keyword '{found_categories[0]}' detected")
    if triggered_severity:
        reason_parts.append(f"severity keywords {', '.join(triggered_severity)} present")

    if not reason_parts:
        # fallback to cite description words
        snippet = description.split(".")[0].strip()
        reason = f"Reason derived from description excerpt: '{snippet}'"
    else:
        reason = " and ".join(reason_parts) + f" from description '{description}'"

    # Ensure reason is one sentence
    if "\n" in reason:
        reason = reason.replace("\n", " ")
    if not reason.endswith("."):
        reason = reason + "."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    errors = []
    rows_processed = 0

    with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV must have header row")

        output_fields = list(reader.fieldnames)
        for required in ["category", "priority", "reason", "flag"]:
            if required not in output_fields:
                output_fields.append(required)

        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()

            for idx, row in enumerate(reader, start=1):
                try:
                    classified = classify_complaint(row)
                    row.update(classified)
                except Exception as ex:
                    errors.append({"row": idx, "error": str(ex)})
                    row.update({
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Failed classification: {str(ex)}",
                        "flag": "NEEDS_REVIEW",
                    })
                writer.writerow(row)
                rows_processed += 1

    return {
        "rows_processed": rows_processed,
        "output_path": output_path,
        "errors": errors,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    result = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
    if result.get("errors"):
        print(f"Completed with {len(result['errors'])} row-level errors. See output for flags.")
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
