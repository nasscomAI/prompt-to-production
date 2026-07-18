"""
UC-0A — Complaint Classifier
This implementation follows the README schema and the enforcement rules from agents.md and skills.md.
"""
import argparse
import csv
import re
from pathlib import Path

ALLOWED_CATEGORIES = {
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
}
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


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row using the fixed schema from the README."""
    complaint_id = str(row.get("complaint_id", "")).strip() or ""
    description = str(row.get("description", "") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description is empty, so the complaint cannot be classified confidently.",
            "flag": "NEEDS_REVIEW",
        }

    normalized = description.casefold()
    priority = "Urgent" if any(keyword in normalized for keyword in SEVERITY_KEYWORDS) else "Standard"

    if any(term in normalized for term in ["music", "noise", "loud"]):
        priority = "Low" if "urgent" not in normalized else "Urgent"

    matches = []

    if re.search(r"\bpothole\b|\broad\b.*\bcrack\b|\btyre\b", normalized):
        matches.append("Pothole")
    if re.search(r"\bflood|flooded|water|inundat|submerged", normalized):
        matches.append("Flooding")
    if re.search(r"\bstreetlight|light|lights|flicker|sparking|dark", normalized):
        matches.append("Streetlight")
    if re.search(r"\bwaste|garbage|bins|dumped|overflow", normalized):
        matches.append("Waste")
    if re.search(r"\bnoise|music|loud|sn noise", normalized):
        matches.append("Noise")
    if re.search(r"\broad\b|\bfootpath\b|\btiles\b|\bsurface\b|\bsinking\b|\bcrack\b", normalized):
        matches.append("Road Damage")
    if re.search(r"\bheritage\b|\bmonument\b|\bhistoric\b", normalized):
        matches.append("Heritage Damage")
    if re.search(r"\bheat\b|\bhot\b|\btemperature\b", normalized):
        matches.append("Heat Hazard")
    if re.search(r"\bdrain\b|\bblock\b|\bclog\b", normalized):
        matches.append("Drain Blockage")

    if len(matches) == 1:
        category = matches[0]
        flag = ""
    elif len(matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if category == "Other" and flag == "":
        flag = "NEEDS_REVIEW"

    if category == "Road Damage" and "pothole" in normalized:
        category = "Pothole"

    if "pothole" in normalized and "road" in normalized and "damage" in normalized:
        category = "Pothole"

    reason = build_reason(description, category)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def build_reason(description: str, category: str) -> str:
    """Construct a single-sentence reason that cites specific words from the description."""
    excerpt = description.strip()
    if not excerpt:
        return "The description is empty, so the complaint cannot be classified confidently."

    if category == "Other":
        return f"The description mentions '{excerpt[:60].rstrip()}…' without enough detail for a confident category assignment."

    key_terms = []
    lowered = description.casefold()
    for term in ["pothole", "flooded", "streetlight", "waste", "noise", "road", "heritage", "heat", "drain", "hazard", "fell", "collapse", "injury", "school", "hospital", "ambulance", "fire"]:
        if term in lowered:
            key_terms.append(term)

    if key_terms:
        key_terms_text = ", ".join(key_terms[:3])
        return f"The description mentions {key_terms_text}, which supports category {category}."

    return f"The description supports category {category} based on the provided complaint text."


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write a results CSV."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with output_file.open("w", encoding="utf-8", newline="") as out_handle:
            writer = csv.DictWriter(out_handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                try:
                    result = classify_complaint(row)
                except Exception:
                    result = {
                        "complaint_id": str(row.get("complaint_id", "")).strip(),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "The row could not be classified because of an unexpected processing error.",
                        "flag": "NEEDS_REVIEW",
                    }
                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
