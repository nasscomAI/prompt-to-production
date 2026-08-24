"""
UC-0A — Complaint Classifier
Rule-based implementation of agents.md enforcement and skills.md contracts.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]
FLAG_REVIEW = "NEEDS_REVIEW"

SEVERITY_PATTERN = re.compile(
    r"\binjur\w*|\bchild\w*|\bschool\w*|\bhospital|\bambulance|\bfire\b|"
    r"\bhazard|\bfell\b|\bcollapse",
    re.IGNORECASE,
)

CATEGORY_PATTERNS = [
    ("Pothole", re.compile(r"\bpotholes?\b", re.I)),
    (
        "Flooding",
        re.compile(r"\bflood\w*|\bwaterlogg\w*|\binundat\w*|"
                   r"\brainwater\b[^.;]{0,30}\b(?:through|across)\b", re.I),
    ),
    (
        "Streetlight",
        re.compile(r"\bstreet\s?lights?|\blights?\s+out\b|\bunlit\b|\bdarkness\b|"
                   r"\bpower\s+(?:cut|outage)\b", re.I),
    ),
    (
        "Waste",
        re.compile(r"\bgarbage\b|\bwaste\b|\btrash\b|\blitter\w*|"
                   r"\bdead\s+(?:animal\w*|tree\w*)|\bbulk\s+waste\b", re.I),
    ),
    (
        "Noise",
        re.compile(r"\bnoise\b|\bnoisy\b|\bloud\b|\bmusic\b|\bamplif\w*|\bband\b|"
                   r"\bdrill\w*|\bidling\b|\bengines?\s+(?:on|running)\b", re.I),
    ),
    (
        "Road Damage",
        re.compile(r"\bcrack\w*|\bsinking\b|\bsubsid\w*|\bbuckl\w*|\bupturn\w*|"
                   r"\bfootpath\b|\btiles?\b|\bcobblestones?\b|\bcollaps\w*|\bcrater\w*", re.I),
    ),
    ("Heritage Damage", re.compile(r"\bheritage\b|\bmonuments?\b", re.I)),
    (
        "Heat Hazard",
        re.compile(r"\bheat\s?-?waves?\b|\bheatwaves?\b|\bmelting\b|\bbubbling\b|"
                   r"\btemperat\w*|°C|\bburns?\b", re.I),
    ),
    (
        "Drain Blockage",
        re.compile(r"\bdrain\w*[^.;]{0,40}?\bblock\w*|\bblock\w*[^.;]{0,40}?\bdrain\w*|"
                   r"\bclogg\w*|\bchok\w*|\bmanholes?\b|\bstormwater\b|"
                   r"\bdraining\s+onto\b", re.I),
    ),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing or empty; routed for manual review.",
            "flag": FLAG_REVIEW,
        }

    evidence = {}
    for category, pattern in CATEGORY_PATTERNS:
        found = [m.group(0) for m in pattern.finditer(description)]
        if found:
            evidence[category] = found

    severity_hits = [m.group(0) for m in SEVERITY_PATTERN.finditer(description)]

    if len(evidence) == 0:
        return {
            "category": "Other",
            "priority": "Urgent" if severity_hits else "Standard",
            "reason": "No known category keywords found in description; "
                      "routed for manual review.",
            "flag": FLAG_REVIEW,
        }

    if len(evidence) > 1:
        parts = [
            "'{}' indicates {}".format(words[0], category)
            for category, words in evidence.items()
        ]
        reason = "Description mentions " + " and ".join(parts) + \
                 "; cannot determine a single category."
        return {
            "category": "Other",
            "priority": "Urgent" if severity_hits else "Standard",
            "reason": reason,
            "flag": FLAG_REVIEW,
        }

    category, words = next(iter(evidence.items()))
    if severity_hits:
        priority = "Urgent"
        reason = "Classified as {} because description mentions '{}'; " \
                 "priority Urgent due to '{}'.".format(
                     category, words[0].lower(), severity_hits[0].lower())
    else:
        priority = "Standard"
        reason = "Classified as {} because description mentions '{}'.".format(
            category, words[0].lower())
    return {"category": category, "priority": priority, "reason": reason,
            "flag": ""}


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Returns the number of rows written.
    """
    source = Path(input_path)
    if not source.is_file():
        sys.exit("Error: input file not found: {}".format(input_path))
    if source.stat().st_size == 0:
        sys.exit("Error: input file is empty: {}".format(input_path))

    try:
        source_handle = open(source, newline="", encoding="utf-8-sig")
    except OSError as exc:
        sys.exit("Error: cannot read input file: {}".format(exc))

    with source_handle:
        reader = csv.DictReader(source_handle)
        if not reader.fieldnames:
            sys.exit("Error: input file has no header row.")
        if "description" not in reader.fieldnames:
            sys.exit("Error: input file missing required 'description' column.")

        target = Path(output_path)
        try:
            target_handle = open(target, "w", newline="", encoding="utf-8")
        except OSError as exc:
            sys.exit("Error: cannot write output file: {}".format(exc))

        written = 0
        with target_handle:
            writer = csv.DictWriter(target_handle,
                                    fieldnames=list(reader.fieldnames) + OUTPUT_FIELDS)
            writer.writeheader()
            for row in reader:
                row.update(classify_complaint(row))
                writer.writerow(row)
                written += 1
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    rows = batch_classify(args.input, args.output)
    print("Done. {} rows classified. Results written to {}".format(rows, args.output))
