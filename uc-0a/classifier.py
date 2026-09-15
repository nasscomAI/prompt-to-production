"""UC-0A municipal complaint classifier.

The rules deliberately use only the complaint row and always emit values from
the fixed assignment taxonomy.
"""

import argparse
import csv
import re
from pathlib import Path


CATEGORIES = {
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
PRIORITIES = {"Urgent", "Standard", "Low"}
REQUIRED_INPUT_FIELDS = {"complaint_id", "description"}

# Severity keywords must trigger Urgent. Each is matched as a whole word so
# "fire" never matches "firewall" and "child" never matches "childcare".
SEVERITY_RE = re.compile(
    r"\b(?:"
    r"injur(?:y|ies|ed)"
    r"|child(?:ren)?"
    r"|schools?"
    r"|hospital(?:s|ised|ized)?"
    r"|ambulances?"
    r"|fires?"
    r"|hazards?"
    r"|fell|fallen"
    r"|collaps(?:e|es|ed|ing)"
    r")\b",
    re.IGNORECASE,
)

# Ordered category rules. Earlier entries win, and every pattern is anchored
# with word boundaries so substring collisions ("flood" in "floodlights",
# "heat" in "theater") do not misclassify.
_CATEGORY_RULES = (
    ("Pothole", (r"\bpotholes?\b",)),
    ("Streetlight", (
        r"\bstreet\s*lights?\b",
        r"\blights?\s+out\b",
        r"\bunlit\b",
        r"\bdarkness\b",
    )),
    ("Drain Blockage", (
        r"\b(?:drain|drainage|stormwater\s+drain|main\s+drain)\b"
        r"[^.!?\n]{0,30}\b(?:blocked|block|clogged|clog)\b",
    )),
    ("Flooding", (
        r"\bfloods?\b",
        r"\bflooded\b",
        r"\bflooding\b",
        r"\bwaterlogged\b",
        r"\brainwater\b",
        r"\bstormwater\b",
    )),
    ("Waste", (
        r"\bgarbage\b",
        r"\bwaste\b",
        r"\brubbish\b",
        r"\bdumped\b",
        r"\bdead\s+animals?\b",
        r"\bbins?\b",
    )),
    ("Noise", (
        r"\bnoise\w*\b",
        r"\bmusic\b",
        r"\bloud\b",
        r"\bmidnight\b",
        r"\bdrilling\b",
        r"\bamplifiers?\b",
        r"\bband\b",
    )),
    ("Heat Hazard", (
        r"\bheat\w*\b",
        r"\bhot\s+pavement\b",
        r"\bmelt(?:ing|ed)?\b",
        r"\btemperatures?\b",
        r"\d+\s*(?:\u00b0|\u00ba)?\s*C\b",
        r"\b\d+\s*degrees?\b",
    )),
    ("Road Damage", (
        r"\broad\s+surface\b",
        r"\broad\s+cracked\b",
        r"\broad\s+damage\b",
        r"\broad\s+collapsed\b",
        r"\broad\s+subsided\b",
        r"\bsinking\b",
        r"\bfootpath\w*\b",
        r"\bmanholes?\b",
        r"\btiles?\s+broken\b",
        r"\bupturned\b",
        r"\bsubsid(?:ed|ence)\b",
        r"\bcollapsed\b",
        r"\bcrater\w*\b",
        r"\bbuckled\b",
    )),
)

_HERITAGE_CONTEXT_RE = re.compile(
    r"\b(?:heritage|historic(?:al)?|monuments?)\b", re.IGNORECASE
)
_HERITAGE_DAMAGE_RE = re.compile(
    r"\b(?:knocked|broken|defaced|removed|damaged|cracked|collapsed|crumbled|"
    r"eroded|vandalised|vandalized|destroyed|deteriorated|chipped|scratched|"
    r"ruined|sinking|subsidence|subsided|not\s+restored|not\s+replaced)\b",
    re.IGNORECASE,
)


def _first_match(text, patterns):
    """Return the exact source span matching the first pattern, else None."""
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _find_severity(description):
    match = SEVERITY_RE.search(description)
    return match.group(0) if match else None


def _evidence_fragment(description, limit=80):
    """Return one short punctuation-safe quote from the description."""
    text = (description or "").strip()
    if not text:
        return ""
    match = re.match(r"^(.*?[.!?])(?:\s|$)", text, re.DOTALL)
    fragment = (match.group(1) if match else text).strip()
    if len(fragment) > limit:
        fragment = fragment[:limit].rstrip(" ,;:")
    return fragment.rstrip(".!?")


def _match_category(description):
    """Return (category, evidence) with heritage damage taking precedence."""
    if _HERITAGE_CONTEXT_RE.search(description):
        damage = _HERITAGE_DAMAGE_RE.search(description)
        if damage:
            return "Heritage Damage", damage.group(0)

    for category, patterns in _CATEGORY_RULES:
        evidence = _first_match(description, patterns)
        if evidence:
            return category, evidence

    return None, None


def _review_result(complaint_id, description, note):
    """Return Other/NEEDS_REVIEW while preserving mandatory urgency."""
    matched_severity = _find_severity(description)
    priority = "Urgent" if matched_severity else "Standard"
    fragment = _evidence_fragment(description)
    clean_note = note.rstrip(".!? ")
    if fragment:
        # A malformed row can still have a perfectly classifiable description;
        # explain the validation problem without claiming the category failed.
        reason = f'{clean_note}; available description evidence is "{fragment}".'
    else:
        reason = f"{clean_note}; the description is missing."
    return {
        "complaint_id": complaint_id,
        "category": "Other",
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW",
    }


def classify_complaint(row):
    """Classify one row and return complaint_id, category, priority, reason, flag."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not complaint_id or not description:
        return _review_result(
            complaint_id,
            description,
            "Required complaint fields are missing or malformed",
        )

    category, evidence = _match_category(description)
    if category is None:
        return _review_result(
            complaint_id,
            description,
            "The complaint is genuinely ambiguous",
        )

    matched_severity = _find_severity(description)
    priority = "Urgent" if matched_severity else "Standard"
    reason = f'Classified as {category} because the description says "{evidence}"'
    if matched_severity:
        reason += f' and includes the severity word "{matched_severity}"'
    reason += "."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


def batch_classify(input_path, output_path):
    """Classify all rows and write one result row for each readable CSV row."""
    source = Path(input_path)
    if not source.is_file():
        raise ValueError(f"Input CSV does not exist: {input_path}")

    with source.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = set(reader.fieldnames or [])
        if not fieldnames:
            raise ValueError("Input CSV has no header row")
        missing = sorted(REQUIRED_INPUT_FIELDS - fieldnames)
        if missing:
            raise ValueError(
                "Input CSV is missing required columns: " + ", ".join(missing)
            )

        results = []
        for row in reader:
            # A None key means the row had columns beyond the header; flag it
            # but still derive urgency and cite the available description.
            if None in row:
                results.append(_review_result(
                    (row.get("complaint_id") or "").strip(),
                    (row.get("description") or "").strip(),
                    "The row has unexpected columns that do not match the header",
                ))
            else:
                results.append(classify_complaint(row))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with destination.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    print(f"Done. Results written to {args.output}")
