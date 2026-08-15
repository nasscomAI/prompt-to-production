"""
UC-0A — Complaint Classifier

Reads a city test CSV (../data/city-test-files/test_[city].csv), classifies
every complaint into the fixed schema from README.md (category / priority /
reason / flag), and writes uc-0a/results_[city].csv.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""

import argparse
import csv
import re

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

CATEGORY_KEYWORDS = {
    "Pothole": ("pothole",),
    "Flooding": ("flood", "flooded", "floods", "waterlogging", "water logged"),
    "Streetlight": (
        "streetlight",
        "streetlights",
        "street light",
        "street lights",
        "lights out",
        "flickering",
        "sparking",
        "lamp",
    ),
    "Waste": (
        "garbage",
        "rubbish",
        "bins",
        "litter",
        "trash",
        "dead animal",
        "waste",
        "dumped",
    ),
    "Noise": ("noise", "music", "loud", "speaker", "party"),
    "Road Damage": (
        "road surface",
        "cracked",
        "sinking",
        "footpath",
        "pavement",
        "tiles",
        "upturned",
    ),
    "Heritage Damage": ("heritage",),
    "Heat Hazard": ("heat", "heatwave", "heat wave", "temperature"),
    "Drain Blockage": ("drain", "drainage", "manhole", "blocked", "blockage", "choked"),
}


def _matches(text: str, keywords) -> tuple:
    found = []
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
            found.append(kw)
    return tuple(found)


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    first_sentence = description.split(".")[0].strip() + "."

    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided to classify.",
            "flag": "NEEDS_REVIEW",
        }

    matched_categories = {
        cat
        for cat, kws in CATEGORY_KEYWORDS.items()
        if _matches(description, kws)
    }

    if len(matched_categories) == 1:
        category = matched_categories.pop()
        flag = ""
        kw = next(
            k for k in CATEGORY_KEYWORDS[category] if _matches(description, (k,))
        )
        reason = f"Category '{category}': matched '{kw}' in \"{first_sentence}\""
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        names = ", ".join(sorted(matched_categories))
        reason = f"Ambiguous: {names} both plausible from \"{first_sentence}\""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Category unknown: no schema keyword matched \"{first_sentence}\""

    severity_hits = _matches(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity_hits else "Standard"
    if severity_hits:
        reason += (
            f" Priority Urgent: severity keyword '{severity_hits[0]}' "
            f"in \"{first_sentence}\""
        )

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError(f"No header row found in {input_path}")
        rows = list(reader)

    out_fieldnames = list(fieldnames) + ["category", "priority", "reason", "flag"]

    classified = 0
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
                classified += 1
            except Exception as exc:
                result = {
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            out = dict(row)
            out.update(result)
            writer.writerow(out)

    print(
        f"Done. Classified {classified}/{len(rows)} rows. "
        f"Results written to {output_path}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
