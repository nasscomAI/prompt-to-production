import argparse
import csv
import os
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

SEVERITY_KEYWORDS = [
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


def classify_complaint(data: dict) -> dict:
    """Skill: classify_complaint

    Classifies a single citizen complaint description row into an allowed category,
    priority level, one-sentence cited reason, and ambiguity flag.
    """
    if not isinstance(data, dict):
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description text.",
            "flag": "NEEDS_REVIEW",
        }

    description = data.get("description")

    if not description or not isinstance(description, str) or not description.strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description text.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.strip()
    text_lower = text.lower()

    # Rule 1: Priority check (Urgent if any severity keyword is present)
    has_severity = any(
        re.search(r"\b" + re.escape(kw) + r"\b", text_lower)
        for kw in SEVERITY_KEYWORDS
    )
    priority = "Urgent" if has_severity else "Standard"

    # Rule 2: Category mapping and ambiguity detection
    category = "Other"
    flag = ""

    # Count matching domain categories
    matches = []
    if re.search(r"\b(pothole|potholes|crater)\b", text_lower):
        matches.append("Pothole")
    if re.search(r"\b(waterlog|waterlogging|flood|flooding|inundat)\b", text_lower):
        matches.append("Flooding")
    if re.search(r"\b(streetlight|street light|light|lamp|darkness)\b", text_lower):
        matches.append("Streetlight")
    if re.search(r"\b(garbage|waste|trash|dump|dumping|litter|rubbish)\b", text_lower):
        matches.append("Waste")
    if re.search(r"\b(noise|loud|music|speaker|blaring)\b", text_lower):
        matches.append("Noise")
    if re.search(r"\b(road|asphalt|tarmac|crack|pavement)\b", text_lower):
        matches.append("Road Damage")
    if re.search(r"\b(heritage|statue|monument|fort|historic)\b", text_lower):
        matches.append("Heritage Damage")
    if re.search(r"\b(heat|sunstroke|extreme heat|wave)\b", text_lower):
        matches.append("Heat Hazard")
    if re.search(r"\b(drain|sewer|gutter|choke|clog|blocked drain)\b", text_lower):
        matches.append("Drain Blockage")

    if len(matches) == 1:
        category = matches[0]
    elif len(matches) > 1:
        category = matches[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Enforce strict taxonomy boundary (no variations/hallucinated sub-categories)
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Rule 3: Single-sentence citation reason
    sentences = [s.strip() for s in re.split(r"(?<=[.!?]) +", text) if s.strip()]
    cited_text = sentences[0] if sentences else text
    reason = f"Cited from description: '{cited_text}'"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> dict:
    """Skill: batch_classify

    Reads an input CSV file, applies classify_complaint sequentially per row,
    and writes structured classification outputs to a target CSV file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found or unreadable: {input_path}")

    # Ensure output destination folder exists
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    rows_processed = 0

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Refuse processing if description column is completely missing
        fieldnames = reader.fieldnames or []
        desc_col = next(
            (col for col in fieldnames if "desc" in col.lower()), None
        )
        if not desc_col:
            raise FileNotFoundError(
                f"Missing required description column in file: {input_path}"
            )

        # Build output header
        out_fields = [f for f in fieldnames if f not in ["category", "priority_flag"]]
        for col in ["category", "priority", "reason", "flag"]:
            if col not in out_fields:
                out_fields.append(col)

        rows_out = []
        for row in reader:
            try:
                description = row.get(desc_col, "")
                result = classify_complaint({"description": description})
            except Exception:
                result = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Failed to parse row.",
                    "flag": "NEEDS_REVIEW",
                }

            row["category"] = result["category"]
            row["priority"] = result["priority"]
            row["reason"] = result["reason"]
            row["flag"] = result["flag"]

            rows_out.append(row)
            rows_processed += 1

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows_out)

    return {
        "rows_processed": rows_processed,
        "output_path": output_path,
        "status": "SUCCESS",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")

    args = parser.parse_args()

    try:
        res = batch_classify(args.input, args.output)
        print(f"Processed {res['rows_processed']} rows -> Saved to {res['output_path']}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)