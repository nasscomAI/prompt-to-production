"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Optional


SEVERITY_KEYWORDS = (
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
)
CATEGORY_RULES = (
    ("Drain Blockage", ("drain blocked", "blocked drain", "drain blockage", "drain clogged")),
    ("Heritage Damage", ("heritage", "historic", "historical building")),
    ("Heat Hazard", ("heatwave", "heat wave", "extreme heat", "heat hazard", "melting", "dangerous temperatures", "unbearable", "temperature", "storing heat", "full sun")),
    ("Pothole", ("pothole", "potholes")),
    ("Flooding", ("flooded", "flooding", "floods", "flood", "waterlogged", "inaccessible after rain")),
    ("Streetlight", ("streetlights out", "streetlight", "streetlights", "street light", "lights out", "light flickering", "lighting", "darkness", "unlit")),
    ("Waste", ("garbage", "waste", "dead animal", "rubbish", "dumped")),
    ("Noise", ("noise", "loud music", "music past midnight", "wedding band", "club music", "sound")),
    ("Road Damage", ("road surface", "road damaged", "cobblestones broken", "cracked", "sinking", "subsided", "manhole", "footpath", "paving", "bench", "tiles broken", "shelter roof", "glass broken")),
)


def _first_evidence(text: str, terms: tuple[str, ...]) -> Optional[str]:
    for term in terms:
        if re.search(r"\b" + re.escape(term) + r"\b", text):
            return term
    return None

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    result = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "The complaint description is missing or does not identify a supported category.",
        "flag": "NEEDS_REVIEW",
    }
    if not description:
        result["reason"] = "The complaint description is missing, so the category cannot be determined."
        return result

    normalized = description.casefold()
    for category, terms in CATEGORY_RULES:
        evidence = _first_evidence(normalized, terms)
        if evidence is not None:
            result["category"] = category
            result["reason"] = f'The description mentions "{evidence}".'
            result["flag"] = ""
            break

    urgent_evidence = _first_evidence(normalized, SEVERITY_KEYWORDS)
    if urgent_evidence is not None:
        result["priority"] = "Urgent"
        result["reason"] = f'{result["reason"][:-1]} and "{urgent_evidence}".'
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    required_fields = {"complaint_id", "description"}
    with open(input_path, "r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        missing_fields = required_fields - set(reader.fieldnames or ())
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Input CSV is missing required field(s): {missing}")

        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                try:
                    writer.writerow(classify_complaint(row))
                except (AttributeError, TypeError, ValueError) as error:
                    writer.writerow({
                        "complaint_id": str(row.get("complaint_id", "")).strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"The row could not be classified: {error}.",
                        "flag": "NEEDS_REVIEW",
                    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
