#!/usr/bin/env python3
"""Municipal complaint classifier."""

import argparse
import csv
import re
import sys
from typing import Dict, List, Optional, Tuple

# Categories and their defining keyword patterns
CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "Pothole": [
        r"\bpotholes?\b",
        r"\bcrater\b",
        r"\bchug-hole\b",
    ],
    "Flooding": [
        r"\bflood(?:ing|ed|s)?\b",
        r"\bwaterlog(?:ged|ging)?\b",
        r"\bstanding water\b",
        r"\binundat(?:ed|ion)\b",
        r"\bsubmerged\b",
    ],
    "Streetlight": [
        r"\bstreet\s*lights?\b",
        r"\blight\s*pole\b",
        r"\blamp\s*post\b",
        r"\bdark street\b",
        r"\bbulb out\b",
    ],
    "Waste": [
        r"\bgarbage\b",
        r"\btrash\b",
        r"\bwaste\b",
        r"\blitter(?:ing)?\b",
        r"\brubbish\b",
        r"\bdump(?:ing|ed)?\b",
        r"\bdebris\b",
    ],
    "Noise": [
        r"\bnoise\b",
        r"\bloud\b",
        r"\bmusic\b",
        r"\bdecibel\b",
        r"\bbarking\b",
        r"\bhonking\b",
    ],
    "Road Damage": [
        r"\broad damage\b",
        r"\bcrack(?:ed|s)? road\b",
        r"\basphalt\b",
        r"\bsinkhole\b",
        r"\bcaved?-in\b",
        r"\bpavement damage\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b",
        r"\bmonument\b",
        r"\bstatue\b",
        r"\bhistoric(?:al)? site\b",
        r"\blandmark\b",
    ],
    "Heat Hazard": [
        r"\bheat\s*wave\b",
        r"\bextreme heat\b",
        r"\bheat stroke\b",
        r"\boverheating\b",
        r"\bscorching\b",
    ],
    "Drain Blockage": [
        r"\bdrain(?:age)?\b",
        r"\bclog(?:ged)? drain\b",
        r"\bblock(?:ed)? drain\b",
        r"\bsewer\b",
        r"\bgutter blocked\b",
        r"\bmanhole\b",
    ],
}

URGENT_PATTERNS = [
    r"\bchild(?:ren)?\b",
    r"\bschool\b",
    r"\bhospital\b",
    r"\baccident\b",
    r"\binjur(?:y|ies|ed)\b",
    r"\bemergency\b",
]

LOW_PATTERNS = [
    r"\bminor\b",
    r"\baesthetic\b",
    r"\bcosmetic\b",
    r"\bslight\b",
    r"\bwhenever possible\b",
    r"\blow priority\b",
]


def _find_matches(text: str, patterns: List[str]) -> List[str]:
    """Finds all unique regex pattern matches in the text."""
    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text, flags=re.IGNORECASE)
        for m in found:
            clean_m = m.strip()
            if clean_m.lower() not in [item.lower() for item in matches]:
                matches.append(clean_m)
    return matches


def classify_complaint(text: str) -> Tuple[str, str, str, str]:
    """Classifies a single municipal complaint.

    Args:
        text: Raw text of the complaint.

    Returns:
        Tuple containing (category, priority, reason, flag).
    """
    if not text or not text.strip():
        return (
            "Other",
            "Low",
            "Complaint text is empty or unreadable.",
            "NEEDS_REVIEW",
        )

    # 1. Determine Category
    matched_categories: List[Tuple[str, List[str]]] = []
    for category, patterns in CATEGORY_PATTERNS.items():
        hits = _find_matches(text, patterns)
        if hits:
            matched_categories.append((category, hits))

    if len(matched_categories) == 1:
        category, cat_matches = matched_categories[0]
        flag = ""
    else:
        # Ambiguous (multiple matches) or zero matches
        category = "Other"
        cat_matches = [hit for _, hits in matched_categories for hit in hits]
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    urgent_matches = _find_matches(text, URGENT_PATTERNS)
    low_matches = _find_matches(text, LOW_PATTERNS)

    if urgent_matches:
        priority = "Urgent"
    elif low_matches:
        priority = "Low"
    else:
        priority = "Standard"

    # 3. Construct Reason quoting found keywords
    quoted_keywords: List[str] = []
    for match in urgent_matches + cat_matches + low_matches:
        quoted_str = f"'{match}'"
        if quoted_str not in quoted_keywords:
            quoted_keywords.append(quoted_str)

    if quoted_keywords:
        quoted_phrase = ", ".join(quoted_keywords)
        if flag == "NEEDS_REVIEW":
            reason = f"Classified based on keywords {quoted_phrase} requiring operational verification."
        else:
            reason = f"Identified {category.lower()} issue based on keywords {quoted_phrase}."
    else:
        reason = "Classified as Other due to absence of definitive category keywords."

    return category, priority, reason, flag


def batch_classify(input_path: str, output_path: str) -> None:
    """Reads complaints from input CSV, classifies them, and writes results to output CSV.

    Args:
        input_path: Filepath to source CSV.
        output_path: Filepath to target CSV.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        infile = open(input_path, mode="r", encoding="utf-8-sig", errors="replace")
    except OSError as err:
        sys.stderr.write(f"Error opening input file: {err}\n")
        sys.exit(1)

    try:
        outfile = open(output_path, mode="w", encoding="utf-8", newline="")
    except OSError as err:
        infile.close()
        sys.stderr.write(f"Error opening output file: {err}\n")
        sys.exit(1)

    with infile, outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        if not reader.fieldnames:
            return

        # Resolve ID and text fields case-insensitively
        id_col: Optional[str] = None
        text_col: Optional[str] = None

        for field in reader.fieldnames:
            normalized = field.lower().strip()
            if normalized in ["complaint_id", "id", "ticket_id"]:
                id_col = field
            elif normalized in ["complaint", "description", "text", "issue"]:
                text_col = field

        # Fallback to first and second columns if not matching standard headers
        if not id_col and len(reader.fieldnames) >= 1:
            id_col = reader.fieldnames[0]
        if not text_col and len(reader.fieldnames) >= 2:
            text_col = reader.fieldnames[1]

        for line_num, row in enumerate(reader, start=2):
            try:
                complaint_id = row.get(id_col, "").strip() if id_col else str(line_num - 1)
                text = row.get(text_col, "") if text_col else ""

                category, priority, reason, flag = classify_complaint(text)

                writer.writerow({
                    "complaint_id": complaint_id,
                    "category": category,
                    "priority": priority,
                    "reason": reason,
                    "flag": flag,
                })
            except Exception as err:
                sys.stderr.write(f"Skipping row {line_num} due to processing error: {err}\n")
                fallback_id = row.get(id_col, f"row_{line_num}") if (id_col and row) else f"row_{line_num}"
                writer.writerow({
                    "complaint_id": fallback_id,
                    "category": "Other",
                    "priority": "Urgent",
                    "reason": f"System encountered processing error: '{err}'.",
                    "flag": "NEEDS_REVIEW",
                })
                continue


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Classify municipal complaints based on issue type and urgency."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file containing complaints.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path where the output CSV file should be written.",
    )

    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()