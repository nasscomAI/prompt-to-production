"""
UC-0A — Complaint Classifier

Deterministic classifier that maps each complaint row from an input CSV to an
exactly allowed category / priority pair, a one-sentence reason quoting words
from the description, and an optional NEEDS_REVIEW flag.

Enforcement (per agents.md / README):
  - category  in {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
                  Heritage Damage, Heat Hazard, Drain Blockage, Other}
  - priority  in {Urgent, Standard, Low}
  - Urgent iff a listed severity keyword appears in the description
  - reason is one sentence and quotes exact words from the description
  - flag is either NEEDS_REVIEW or blank

Standard library only.
"""
import argparse
import csv
import sys

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
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": [
        "flood", "flooding", "flooded", "floods", "water logging",
        "waterlogged", "inundated",
    ],
    "Streetlight": [
        "streetlight", "streetlights", "street light", "street lights",
        "street lamp", "street lamps", "lamp post", "lamp posts",
        "street lighting", "lighting", "unlit", "dark", "darkness",
        "lights out", "no light",
    ],
    "Waste": [
        "garbage", "waste", "trash", "litter", "refuse", "dumping",
        "dumped", "dump", "debris", "dead animal", "dead animals",
    ],
    "Noise": [
        "noise", "noisy", "loud", "music", "honk", "honking", "blaring",
        "band", "amplifier", "amplifiers", "drilling", "idling", "audible",
    ],
    "Road Damage": [
        "road damage", "road surface", "road crack", "road cracked",
        "road buckled", "road collapsed", "road subsided", "crack", "cracked",
        "cracks", "asphalt", "pavement", "paving", "footpath", "sinking",
        "subsidence", "subsided", "buckled", "crater", "collapsed",
    ],
    "Heritage Damage": [
        "heritage", "historic", "historical", "monument", "monuments",
        "ancient", "step well", "temple",
    ],
    "Heat Hazard": [
        "heat", "heatwave", "heat wave", "sunstroke", "heat stroke",
        "heatstroke", "extreme heat", "melting", "temperature",
        "temperatures", "\u00b0c", "full sun", "sunlight",
    ],
    "Drain Blockage": [
        "drain", "drains", "drainage", "sewer", "sewage", "clog",
        "clogged", "blocked", "manhole", "manholes", "stormwater drain",
    ],
}


def _quote_occurrences(description, desc_lower, keywords):
    """Return single-quoted exact substrings of `description` for keywords found.

    Extracts the words verbatim (original casing) so the reason cites exact
    words from the complaint description.
    """
    quotes = []
    for keyword in keywords:
        idx = desc_lower.find(keyword)
        if idx >= 0:
            exact = description[idx:idx + len(keyword)]
            quoted = "'{0}'".format(exact)
            if quoted not in quotes:
                quotes.append(quoted)
    return quotes


def _generate_reason(description, desc_lower, matched_categories, found_severity,
                     ambiguous, category):
    quoted_category_words = []
    for keywords in matched_categories.values():
        quoted_category_words.extend(
            _quote_occurrences(description, desc_lower, keywords))
    quoted_words = _quote_occurrences(description, desc_lower, found_severity)
    for word in quoted_category_words:
        if word not in quoted_words:
            quoted_words.append(word)
    cited = ", ".join(quoted_words)

    if ambiguous:
        candidate_names = " and ".join(matched_categories.keys())
        return ("Complaint mentions {0}, which could indicate {1}, making the "
                "correct category ambiguous and requiring review.".format(
                    cited, candidate_names))

    if category == "Other" and not matched_categories:
        preview = description.strip()
        for separator in (".", "!", "?"):
            cut = preview.find(separator)
            if cut >= 0:
                preview = preview[:cut]
                break
        preview = preview.strip()
        if len(preview) > 90:
            preview = preview[:90].rstrip() + "\u2026"
        return ("Complaint '{0}' does not clearly match any allowed "
                "category.".format(preview))

    if found_severity:
        return ("Complaint mentions {0}, indicating a {1} issue requiring "
                "urgent attention.".format(cited, category))

    return ("Complaint mentions {0}, indicating a {1} issue.".format(
        cited, category))


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row into category, priority, reason, flag."""
    description = row.get("description")

    if not isinstance(description, str) or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "invalid input: missing description",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    is_urgent = bool(found_severity)

    matched_categories = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            matched_categories[category] = hits

    ambiguous = False
    category = "Other"

    if len(matched_categories) == 1:
        category = list(matched_categories.keys())[0]
    elif len(matched_categories) > 1:
        ranked = sorted(matched_categories.items(),
                        key=lambda item: len(item[1]), reverse=True)
        if len(ranked[0][1]) > len(ranked[1][1]):
            category = ranked[0][0]
        else:
            ambiguous = True
            category = "Other"

    if is_urgent:
        priority = "Urgent"
    elif category == "Other" or ambiguous:
        priority = "Low"
    else:
        priority = "Standard"

    flag = "NEEDS_REVIEW" if ambiguous else ""

    reason = _generate_reason(description, desc_lower, matched_categories,
                              found_severity, ambiguous, category)

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read an input CSV, classify every row, write the results CSV.

    Returns a summary dict on success. On hard errors (missing file, malformed
    CSV, missing description column) it prints a clear error and exits without
    writing partial output. Malformed rows are classified with the fallback
    tuple per skills.md and processing continues.
    """
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                print("Error: empty or malformed CSV: {0}".format(input_path),
                      file=sys.stderr)
                sys.exit(1)
            fieldnames = list(reader.fieldnames)
            rows = list(reader)
    except (csv.Error, OSError, UnicodeDecodeError) as exc:
        print("Error: failed to read input CSV '{0}': {1}".format(
            input_path, exc), file=sys.stderr)
        sys.exit(1)

    if "description" not in fieldnames:
        print("Error: input CSV '{0}' is missing the required 'description' "
              "column".format(input_path), file=sys.stderr)
        sys.exit(1)

    output_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]

    rows_processed = 0
    rows_flagged = 0
    diagnostics = []
    output_rows = []

    for index, row in enumerate(rows, start=1):
        rows_processed += 1
        result = classify_complaint(row)

        output_row = dict(row)
        output_row["category"] = result["category"]
        output_row["priority"] = result["priority"]
        output_row["reason"] = result["reason"]
        output_row["flag"] = result["flag"]
        output_rows.append(output_row)

        if result["flag"] == "NEEDS_REVIEW":
            rows_flagged += 1
            row_id = row.get("complaint_id") or row.get("id") or str(index)
            entry = "Row {0}: NEEDS_REVIEW - {1}".format(row_id, result["reason"])
            diagnostics.append(entry)
            print(entry, file=sys.stderr)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=output_fieldnames,
                                    extrasaction="ignore")
            writer.writeheader()
            for output_row in output_rows:
                writer.writerow(output_row)
    except (OSError, csv.Error) as exc:
        print("Error: failed to write results CSV '{0}': {1}".format(
            output_path, exc), file=sys.stderr)
        sys.exit(1)

    return {
        "output_path": output_path,
        "rows_processed": rows_processed,
        "rows_flagged": rows_flagged,
        "diagnostics": diagnostics,
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True,
                        help="Path to test_[city].csv")
    parser.add_argument("--output", required=True,
                        help="Path to write results CSV")
    args = parser.parse_args()

    result = batch_classify(args.input, args.output)
    if result is not None:
        print("Done. Results written to {0}".format(result["output_path"]))


if __name__ == "__main__":
    main()