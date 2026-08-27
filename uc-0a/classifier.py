"""UC-0A citizen complaint classifier."""

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

CATEGORY_PATTERNS = {
    "Pothole": (r"\bpotholes?\b",),
    "Flooding": (
        r"\bflood(?:ed|ing|s)?\b",
        r"\brainwater\b",
        r"\bdraining\s+(?:directly\s+)?(?:onto|into)\b",
    ),
    "Streetlight": (
        r"\bstreet ?lights?\b",
        r"\blights?\s+out\b",
        r"\bunlit\b",
        r"\bdarkness\b",
    ),
    "Waste": (r"\bwaste\b", r"\bgarbage\b", r"\bbins?\b", r"\bdead animal\b"),
    "Noise": (
        r"\bnoise\b",
        r"\bmusic\b",
        r"\bband\b",
        r"\bdrilling\b",
        r"\bamplifiers?\b",
        r"\bidling\b",
    ),
    "Road Damage": (
        r"\broad\s+(?:surface\s+)?(?:cracked|sinking|collapsed|subsided|buckled)\b",
        r"\broad\s+subsidence\b",
        r"\bfootpath\b",
        r"\b(?:tiles|paving|cobblestones?)\s+(?:broken|upturned|removed)\b",
        r"\bcrater\b",
        r"\b(?:surface|tarmac)\s+(?:cracked|sinking)\b",
    ),
    "Heritage Damage": (
        r"\bheritage\s+(?:lamp post|building|stone)\b",
        r"\bhistoric\s+(?:tram road|building|cobblestones?)\b",
        r"\bheritage\s+residential\s+building\b",
    ),
    "Heat Hazard": (
        r"\bheat(?:wave)?\b",
        r"\btemperature\b",
        r"\b(?:melting|unbearable|dangerous)\s+temperatures?\b",
        r"\b\d+\s*(?:[^A-Za-z0-9\s]\s*)?c\b",
        r"\b(?:storing\s+heat|burns?\s+on\s+contact)\b",
    ),
    "Drain Blockage": (
        r"\bdrain\s+(?:completely\s+)?blocked\b",
        r"\bblocked\s+(?:with\s+\w+\s+)?(?:stormwater\s+)?drain\b",
        r"\bmanhole\s+cover\s+missing\b",
    ),
}


def _first_match(patterns: tuple[str, ...], description: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row into the required output fields."""
    description = str(row.get("description") or "").strip()
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing, so no service category can be supported.",
            "flag": "NEEDS_REVIEW",
        }

    severity_match = next(
        (keyword for keyword in SEVERITY_KEYWORDS if keyword in description.lower()),
        None,
    )
    priority = "Urgent" if severity_match else "Standard"
    evidence = {
        category: (match, description.lower().index(match.lower()))
        for category, patterns in CATEGORY_PATTERNS.items()
        if (match := _first_match(patterns, description))
    }

    if "Heritage Damage" in evidence:
        category = "Heritage Damage"
        category_match = evidence[category][0]
        flag = ""
        reason = (
            f'Assigned {category} with {priority} priority because the description contains '
            f'"{category_match}"'
        )
    elif evidence:
        first_position = min(position for _, position in evidence.values())
        leading_categories = [
            category
            for category, (_, position) in evidence.items()
            if position == first_position
        ]
        if len(leading_categories) == 1:
            category = leading_categories[0]
            category_match = evidence[category][0]
            flag = ""
            reason = (
                f'Assigned {category} with {priority} priority because the description contains '
                f'"{category_match}"'
            )
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            matches = ", ".join(f'"{evidence[item][0]}"' for item in leading_categories)
            reason = (
                f'Assigned Other with {priority} priority because {matches} support multiple '
                "service categories equally"
            )
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        excerpt = re.sub(r"[.!?]", ",", " ".join(description.split()[:8]))
        reason = (
            f'Assigned Other with {priority} priority because "{excerpt}" does not identify '
            "a supported service category"
        )

    if severity_match:
        reason += f' and "{severity_match}" requires Urgent priority'
    else:
        reason += " and no severity keyword is present"
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": f"{reason}.",
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """Read a complaint CSV, classify every row, and write the combined output."""
    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if not reader.fieldnames or "description" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a description column.")
        rows = list(reader)

    fieldnames = list(reader.fieldnames)
    for fieldname in ("category", "priority", "reason", "flag"):
        if fieldname not in fieldnames:
            fieldnames.append(fieldname)

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            classification = classify_complaint(row)
            row.update({key: value for key, value in classification.items() if key != "complaint_id"})
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
