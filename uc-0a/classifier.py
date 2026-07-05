"""
UC-0A - Complaint Classifier
"""

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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

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

CATEGORY_KEYWORDS = {
    "Pothole": [
        "deep pothole",
        "pothole",
        "tyre damage",
        "tire damage",
        "crater",
    ],
    "Flooding": [
        "underpass flooded",
        "flooded",
        "floods",
        "flood",
        "waterlogged",
        "water logging",
        "standing in water",
        "knee-deep",
        "rain",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "lights out",
        "street, lights out",
        "lamp",
        "dark",
        "flickering",
        "sparking",
    ],
    "Waste": [
        "garbage bins",
        "garbage",
        "dead animal",
        "waste",
        "trash",
        "animal",
        "dumped",
        "smell",
    ],
    "Noise": [
        "playing music",
        "music",
        "noise",
        "speaker",
        "loud",
    ],
    "Road Damage": [
        "road surface",
        "cracked",
        "sinking",
        "footpath",
        "tiles",
        "manhole cover",
        "manhole",
        "cover missing",
    ],
    "Heritage Damage": [
        "heritage damage",
        "damaged heritage",
        "historic",
        "monument",
        "crack in heritage",
        "cracks in heritage",
    ],
    "Heat Hazard": [
        "heat hazard",
        "heatwave",
        "heat wave",
        "extreme heat",
        "high temperature",
        "no shade",
        "dehydration",
    ],
    "Drain Blockage": [
        "drain blocked",
        "blocked drain",
        "blockage",
        "clogged drain",
        "drainage",
    ],
}

CATEGORY_PRECEDENCE = [
    "Pothole",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Flooding",
    "Other",
]

STANDARD_SIGNALS = [
    "affected",
    "not removed",
    "overflowing",
    "dumped",
    "playing music",
    "dark at night",
    "cracked",
    "sinking",
    "inaccessible",
    "commuters stranded",
]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def keyword_pattern(keyword: str) -> re.Pattern:
    escaped = re.escape(keyword.lower()).replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])")


def find_keyword(text: str, keywords: list[str]) -> str | None:
    for keyword in keywords:
        if keyword_pattern(keyword).search(text):
            return keyword
    return None


def find_severity_keyword(text: str) -> str | None:
    for keyword in SEVERITY_KEYWORDS:
        match = re.search(rf"(?<![a-z0-9]){re.escape(keyword)}[a-z]*", text)
        if match:
            return match.group(0)
    return None


def determine_category(description: str) -> tuple[str, str]:
    text = normalize_text(description)
    matches: dict[str, str] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        evidence = find_keyword(text, keywords)
        if evidence:
            matches[category] = evidence

    if not matches:
        return "Other", "NEEDS_REVIEW"

    if len(matches) == 1:
        category = next(iter(matches))
        return category, ""

    if "Flooding" in matches and "Drain Blockage" in matches:
        return "Flooding", "NEEDS_REVIEW"

    best = sorted(matches, key=lambda item: CATEGORY_PRECEDENCE.index(item))[0]
    return best, "NEEDS_REVIEW"


def determine_priority(description: str, category: str) -> str:
    text = normalize_text(description)
    if find_severity_keyword(text):
        return "Urgent"

    if find_keyword(text, STANDARD_SIGNALS):
        return "Standard"

    if re.search(r"(?<![a-z0-9])\d+\s*(day|days|week|weeks|hour|hours|hrs)(?![a-z0-9])", text):
        return "Standard"

    if category != "Other":
        return "Standard"

    return "Low"


def category_evidence(description: str, category: str) -> str:
    text = normalize_text(description)
    if category in CATEGORY_KEYWORDS:
        evidence = find_keyword(text, CATEGORY_KEYWORDS[category])
        if evidence:
            return evidence
    return "description"


def first_description_words(description: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", description or "")
    return " ".join(words[:4]) if words else "missing description"


def priority_evidence(description: str, priority: str, category: str) -> str:
    text = normalize_text(description)
    if priority == "Urgent":
        return find_severity_keyword(text) or "urgent risk"
    if priority == "Standard":
        return find_keyword(text, STANDARD_SIGNALS) or category_evidence(description, category)
    return first_description_words(description)


def generate_reason(description: str, category: str, priority: str, flag: str) -> str:
    cat_words = category_evidence(description, category)
    pri_words = priority_evidence(description, priority, category)
    review_note = " and flagged for review due to ambiguous category evidence" if flag else ""
    return f"Classified as {category} because the description mentions '{cat_words}', with {priority} priority from '{pri_words}'{review_note}."


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    category, flag = determine_category(description)
    priority = determine_priority(description, category)
    reason = generate_reason(description, category, priority, flag)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    with open(input_file, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError("Input CSV must contain a header row.")

        fieldnames = [
            name
            for name in reader.fieldnames
            if name not in {"category", "priority", "priority_flag", "reason", "flag"}
        ]
        fieldnames += ["category", "priority", "reason", "flag"]

        rows = []
        for row in reader:
            try:
                result = classify_complaint(row)
                row["category"] = result["category"]
                row["priority"] = result["priority"]
                row["reason"] = result["reason"]
                row["flag"] = result["flag"]
            except Exception as exc:
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = f"Classified as Other because row processing failed with '{exc}'."
                row["flag"] = "NEEDS_REVIEW"
            rows.append(row)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Output CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
