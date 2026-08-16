"""
UC-0A — Complaint Classifier
Implements the enforcement rules from agents.md:
- category is exactly one of the 10 allowed strings — no variations
- priority is Urgent on severity keywords, otherwise Standard
- reason cites specific words from the description
- genuinely ambiguous rows are marked Other + flag NEEDS_REVIEW, never guessed
"""
import argparse
import csv

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole"],
    "Flooding": ["flood", "water logging", "waterlog", "knee-deep", "knee deep", "submerged"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "flicker", "spark", "lamp"],
    "Waste": ["garbage", "waste", "bin", "bins", "dead animal", "carcass", "trash", "dumped"],
    "Noise": ["noise", "music", "loud", "speaker", "dj", "honk"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath", "pavement", "tiles", "rutted"],
    "Heritage Damage": ["heritage", "monument", "listed building"],
    "Heat Hazard": ["heat", "overheat"],
    "Drain Blockage": ["drain", "manhole", "sewer", "drainage", "clogged", "choked"],
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    text = description.lower()

    matched = {cat: [kw for kw in kws if kw in text] for cat, kws in CATEGORY_KEYWORDS.items()}
    matched = {cat: kws for cat, kws in matched.items() if kws}

    severity = [kw for kw in SEVERITY_KEYWORDS if kw in text]
    priority = "Urgent" if severity else "Standard"
    flag = ""

    if not matched:
        category = "Other"
        reason = "No classification keyword was found in the description, so it was flagged for review."
        flag = "NEEDS_REVIEW"
    else:
        ranked = sorted(((cat, len(kws)) for cat, kws in matched.items()), key=lambda kv: kv[1], reverse=True)
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            ties = [cat for cat, score in ranked if score == ranked[0][1]]
            matched_words = ", ".join(f'"{kw}"' for cat in ties for kw in matched[cat])
            category = "Other"
            reason = (f"Ambiguous: equal evidence for {' and '.join(ties)} "
                      f"({matched_words}) in the description, so it was flagged for review.")
            flag = "NEEDS_REVIEW"
        else:
            category = ranked[0][0]
            words = ", ".join(f'"{kw}"' for kw in matched[category])
            reason = f"Category '{category}' is supported by {words} in the description."

    if severity:
        triggers = ", ".join(f'"{kw}"' for kw in severity)
        reason += f" Priority is Urgent because the description contains {triggers}."

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Validates columns, flags ambiguous rows, never drops rows.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "description" not in reader.fieldnames:
            raise ValueError("Input CSV must have a header row with a 'description' column.")
        rows = list(reader)

    output_fields = list(reader.fieldnames) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        for i, row in enumerate(rows, start=1):
            out = dict(row)
            try:
                out.update(classify_complaint(row))
            except Exception as exc:
                out.update({"category": "Other",
                            "priority": "Standard",
                            "reason": f"Row {i} could not be classified ({exc}); flagged for review.",
                            "flag": "NEEDS_REVIEW"})
            writer.writerow(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
