"""
UC-0A - Complaint Classifier
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

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

CATEGORY_PATTERNS = [
    ("Pothole", [r"\bpothole\b"]),
    ("Flooding", [r"\bflood", r"standing in water", r"water.?logged", r"\bunderpass flooded\b"]),
    ("Streetlight", [r"streetlight", r"lights? out", r"flickering", r"sparking"]),
    ("Waste", [r"garbage", r"\bbins?\b", r"waste", r"dumped", r"dead animal", r"smell affecting"]),
    ("Noise", [r"\bmusic\b", r"\bnoise\b", r"past midnight", r"loudspeaker"]),
    ("Road Damage", [r"road surface", r"\bcracked\b", r"\bsinking\b", r"tiles broken", r"footpath", r"upturned"]),
    ("Heritage Damage", [r"heritage damage", r"monument", r"heritage structure", r"old city wall"]),
    ("Heat Hazard", [r"\bheat\b", r"heatwave", r"sun exposure", r"no shade"]),
    ("Drain Blockage", [r"drain blocked", r"drainage blocked", r"clogged drain", r"manhole", r"sewer overflow"]),
]


def normalize_text(value: str) -> str:
    text = value or ""
    text = text.lower()
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", text).strip()


def collect_matches(description: str) -> list[str]:
    matches: list[str] = []
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, description):
                matches.append(category)
                break
    return matches


def extract_evidence(description: str) -> str:
    tokens = re.findall(r"[a-z0-9'-]+", description)
    snippet = " ".join(tokens[:8]).strip()
    return snippet or "description text"


def classify_complaint(row: dict) -> dict:
    complaint_id = (row.get("complaint_id") or "").strip()
    description_raw = (row.get("description") or "").strip()
    description = normalize_text(description_raw)

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Marked Other because the description text is missing.",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = collect_matches(description)
    flag = ""

    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        if "Drain Blockage" in matched_categories and "Flooding" in matched_categories:
            category = "Drain Blockage"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"

    priority = "Urgent" if any(keyword in description for keyword in SEVERITY_KEYWORDS) else "Standard"
    if category == "Other" and flag == "NEEDS_REVIEW" and priority == "Standard":
        priority = "Low"

    evidence = extract_evidence(description)
    if flag == "NEEDS_REVIEW":
        reason = f'Marked {category} because "{evidence}" is missing a single clear category signal.'
    else:
        reason = f'Assigned {category} because the description says "{evidence}".'

    return {
        "complaint_id": complaint_id,
        "category": category if category in ALLOWED_CATEGORIES else "Other",
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # pragma: no cover - defensive path
            results.append(
                {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f'Marked Other because row processing failed: "{exc}".',
                    "flag": "NEEDS_REVIEW",
                }
            )

    with output_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["complaint_id", "category", "priority", "reason", "flag"],
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
