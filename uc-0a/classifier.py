"""
UC-0A Complaint Classifier.
Classifies citizen complaint rows into an operational category, response
priority, one-sentence justification citing the description verbatim, and an
ambiguity flag, per uc-0a/agents.md enforcement rules.
"""
import argparse
import csv
import re
import sys

CATEGORIES = [
    "Pothole",
    "Flooding",
    "Drain Blockage",
    "Streetlight",
    "Noise",
    "Heat Hazard",
    "Heritage Damage",
    "Road Damage",
    "Waste",
]

CATEGORY_PATTERNS = {
    "Pothole": [r"\bpotholes?\b"],
    "Flooding": [r"\bflood\w*\b", r"\bwaterlog\w*\b", r"\brainwater\b"],
    "Drain Blockage": [r"\bdrain\w*\b", r"\bblocked?\w*\b|\bclogg?ed\b|\bchoked?\b"],
    "Streetlight": [
        r"\bstreet\s?lights?\b",
        r"\blights? out\b|\bunlit\b|\bdarkness\b|\bdark at night\b",
        r"\blamp ?posts?\b",
    ],
    "Noise": [
        r"\bnoise\b|\bloud\b",
        r"\bmusic\b|\bamp\w*ifiers?\b|\bband playing\b|\bloudspeakers?\b",
        r"\bdrilling\b|\bidling\b|\bhonk\w*\b",
        r"\bmidnight\b|\bat \d{1,2}\s?(am|pm)\b",
    ],
    "Heat Hazard": [
        r"\bheat\w*\b",
        r"\btemperatur\w*\b|\b\d+\s?°?C\b",
        r"\bmelt\w*\b|\bscorch\w*\b|\bbubbl\w*\b|\bstoring heat\b",
    ],
    "Heritage Damage": [
        r"\bheritage\b|\bhistoric\b",
        r"\bmonuments?\b|\bforts?\b|\bpalaces?\b|\bstep wells?\b|\bancient\b|\bcobblestones?\b",
        r"\bdefaced\b|\bknocked over\b|\bbroken up\b|\bnot replaced\b|\bnot restored\b",
    ],
    "Road Damage": [
        r"\bfootpath\b|\bpavement\b",
        r"\bcracked?\b|\bsubside\w*\b|\bbuckled?\b|\bcollaps\w*\b|\bcrater\b|\bsink\w*\b|\bcave.?in\b|\bupturned\b",
        r"\bdividers?\b|\bmanholes?\b",
    ],
    "Waste": [
        r"\bwaste\b|\bgarbage\b|\brubbish\b|\btrash\b|\blitter\b",
        r"\boverflow\w*\b|\bnot cleared\b|\buncleared\b|\bdump(ed|ing)?\b|\bpiles?\b",
        r"\bdead animal\b|\bbins?\b",
    ],
}

SEVERITY_PATTERN = re.compile(
    r"injur\w*|child\w*|school\w*|hospital\w*|ambulances?|fires?|hazards?\w*|collaps\w*|\bfell\b",
    re.IGNORECASE,
)

LOW_PRIORITY_PATTERN = re.compile(
    r"\bresolved\b|\balready\s(?:fixed|repaired|cleared|cleaned)\b|\bno longer\b|\bminor\b",
    re.IGNORECASE,
)

OUTPUT_COLUMNS = ["complaint_id", "category", "priority", "reason", "flag"]
MAX_CITED_TERMS = 3


def _find_terms(description, patterns):
    terms = []
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if not match:
            continue
        term = match.group(0)
        lowered = term.lower()
        if any(lowered in seen.lower() or seen.lower() in lowered for seen in terms):
            continue
        terms.append(term)
    return terms


def _quote(terms):
    shown = terms[:MAX_CITED_TERMS]
    quoted = ", ".join('"%s"' % term for term in shown)
    return quoted


def _one_sentence(text):
    return text.strip().rstrip(".") + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint row.
    Returns dict with keys: complaint_id, category, priority, reason, flag.
    Never raises: falls back to Other + NEEDS_REVIEW on unusable input.
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    try:
        description = (row.get("description") or "").strip()
    except AttributeError:
        description = ""

    fallback = {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": "Standard",
        "reason": "Description missing or unreadable; information needed to determine a category.",
        "flag": "NEEDS_REVIEW",
    }
    if not description:
        return fallback

    scored = []
    for category in CATEGORIES:
        terms = _find_terms(description, CATEGORY_PATTERNS[category])
        if terms:
            scored.append((len(terms), CATEGORIES.index(category), category, terms))

    severity_matches = SEVERITY_PATTERN.findall(description)
    low_matches = LOW_PRIORITY_PATTERN.findall(description)

    if not scored:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if severity_matches else "Standard",
            "reason": "Description lacks recognizable category indicators; information about the reported problem type is missing.",
            "flag": "NEEDS_REVIEW",
        }

    scored.sort(key=lambda item: (-item[0], item[1]))
    top_score, _, category, terms = scored[0]
    runner_up_score = scored[1][0] if len(scored) > 1 else 0

    ambiguous = len(scored) > 1 and runner_up_score >= 1 and top_score - runner_up_score <= 1

    if severity_matches:
        priority = "Urgent"
        extra = [term for term in severity_matches if term.lower() not in [t.lower() for t in terms]]
        priority_note = "; marked Urgent due to %s" % _quote(extra) if extra else ""
    elif low_matches:
        priority = "Low"
        priority_note = "; set to Low as impact reads as minor"
    else:
        priority = "Standard"
        priority_note = ""

    reason = _one_sentence(
        "%s supported by %s in the description%s" % (category, _quote(terms), priority_note)
    )
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if ambiguous else "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never drops rows: malformed rows are written back as Other + NEEDS_REVIEW.
    """
    try:
        handle = open(input_path, "r", encoding="utf-8-sig", newline="")
    except OSError as error:
        print("Error: cannot read input file %s (%s)" % (input_path, error))
        sys.exit(1)

    results = []
    with handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = {key: value for key, value in row.items() if key is not None}
            try:
                results.append(classify_complaint(normalized))
            except Exception:
                results.append(
                    {
                        "complaint_id": (normalized.get("complaint_id") or "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Row malformed; information needed to determine a category.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", encoding="utf-8", newline="") as out_handle:
        writer = csv.DictWriter(out_handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)
