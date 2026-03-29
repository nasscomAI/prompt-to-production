"""
UC-0A — Complaint Classifier
Build using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys
from typing import Dict, List, Optional

CATEGORY_KEYWORDS = [
    ("Pothole", [r"\bpothole\b", r"\bpot hole\b", r"\broad hole\b", r"\bsinkhole\b"]),
    ("Flooding", [r"\bflood\b", r"\bflooding\b", r"\bwater logging\b", r"\bwaterlogging\b", r"\bstanding water\b", r"\bwater accumulat(?:ion|ing)\b"]),
    ("Streetlight", [r"\bstreetlight\b", r"\bstreet light\b", r"\blamp post\b", r"\blamp-post\b", r"\bdark street\b", r"\blight not working\b", r"\bno lights\b"]),
    ("Waste", [r"\bgarbage\b", r"\btrash\b", r"\blitter\b", r"\bwaste\b", r"\bbin\b", r"\bdumping\b", r"\bheap of waste\b"]),
    ("Noise", [r"\bnoise\b", r"\bhonking\b", r"\bloud music\b", r"\bsound pollution\b", r"\bshouting\b", r"\bconstruction noise\b"]),
    ("Road Damage", [r"\broad damage\b", r"\bdamaged road\b", r"\bcracked road\b", r"\bbroken pavement\b", r"\broad crack\b", r"\broad collapse\b", r"\bfissure\b"]),
    ("Heritage Damage", [r"\bheritage\b", r"\bmonument\b", r"\bstatue\b", r"\bhistoric\b", r"\btemple\b", r"\barchaeological\b"]),
    ("Heat Hazard", [r"\bheat\b", r"\bhot\b", r"\bburning\b", r"\bscorching\b", r"\bheat hazard\b", r"\bheatwave\b"]),
    ("Drain Blockage", [r"\bdrain\b", r"\bblocked drain\b", r"\bclogged drain\b", r"\bsewage\b", r"\bstorm drain\b", r"\bwater clog\b"]),
]

SEVERITY_KEYWORDS = [
    r"\binjury\b",
    r"\bchild\b",
    r"\bschool\b",
    r"\bhospital\b",
    r"\bambulance\b",
    r"\bfire\b",
    r"\bhazard\b",
    r"\bfell\b",
    r"\bcollapse\b",
]

ALLOWED_CATEGORIES = {"Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"}
ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}


def _normalize_text(text: str) -> str:
    return text.strip().lower()


def _find_description(row: Dict[str, str]) -> Optional[str]:
    for key in ["description", "complaint", "details", "issue", "text"]:
        value = row.get(key)
        if value and value.strip():
            return value.strip()
    for value in row.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _matches(patterns: List[str], text: str) -> List[str]:
    matches = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            matches.append(pattern)
    return matches


def _extract_keywords(description: str, limit: int = 2) -> List[str]:
    terms = re.findall(r"\b[a-z]{3,}\b", description.lower())
    seen = []
    for term in terms:
        if term not in seen:
            seen.append(term)
        if len(seen) >= limit:
            break
    return seen


def _reason_text(category: str, description: str, matched_keywords: List[str]) -> str:
    if category != "Other" and matched_keywords:
        sample = ", ".join(matched_keywords[:2])
        return f"The description mentions {sample}, indicating {category}."
    if description:
        snippet = " ".join(_extract_keywords(description, limit=2))
        if snippet:
            return f"The description includes {snippet}, but the category is not clearly one of the allowed options."
    return "The complaint description is ambiguous and needs review."


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    description = _find_description(row) or ""
    normalized = _normalize_text(description)

    if not normalized:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided, so the complaint is classified as Other.",
            "flag": "NEEDS_REVIEW",
        }

    category_matches = []
    matched_keywords: List[str] = []

    for category, patterns in CATEGORY_KEYWORDS:
        if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in patterns):
            category_matches.append(category)
            for pattern in patterns:
                if re.search(pattern, normalized, flags=re.IGNORECASE):
                    keyword = pattern.strip(r"\b").replace("\\", "")
                    matched_keywords.append(keyword)
            if len(category_matches) > 1:
                break

    if len(category_matches) == 1:
        category = category_matches[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    priority = "Urgent" if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in SEVERITY_KEYWORDS) else "Standard"
    reason = _reason_text(category, description, matched_keywords)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV is missing header row")

        input_rows = list(reader)

    output_rows = []
    for index, row in enumerate(input_rows, start=2):
        if not row or all((value is None or not str(value).strip()) for value in row.values()):
            print(f"Skipping invalid row at line {index}", file=sys.stderr)
            continue

        result = classify_complaint(row)
        output_row = {}
        if "complaint_id" in row:
            output_row["complaint_id"] = row["complaint_id"]
        output_row.update(result)
        output_rows.append(output_row)

    fieldnames = []
    if output_rows and "complaint_id" in output_rows[0]:
        fieldnames.append("complaint_id")
    fieldnames.extend(["category", "priority", "reason", "flag"])

    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for output_row in output_rows:
            writer.writerow(output_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
