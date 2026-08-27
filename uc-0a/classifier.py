"""
UC-0A — Complaint Classifier (rule-based, no external API required)
"""
import argparse
import csv
import re
import sys

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# Ordered: first matching category wins — specific phrases before generic words
CATEGORY_RULES = [
    ("Pothole",         ["pothole", "pot hole"]),
    ("Flooding",        ["flood", "waterlog", "waterlogged", "inundat", "stagnant water"]),
    ("Drain Blockage",  ["blocked drain", "drain block", "drain choke", "sewer block",
                         "drain overflow", "sewer", "drain"]),
    ("Noise",           ["noise", "music", "audible", "loud", "decibel", "blaring",
                         "amplif", "drill", "loudspeaker"]),
    ("Waste",           ["waste", "garbage", "trash", "rubbish", "litter",
                         "refuse", "dumping", "waste bin", "dead animal"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "unlit",
                         "wiring theft", "no light", "lights out", "light out", "darkness"]),
    ("Heritage Damage", ["heritage damage", "heritage structure", "heritage wall",
                         "heritage building", "ancient", "monument", "step well", "listed building"]),
    ("Heat Hazard",     ["heatwave", "heat wave", "temperature", "melting",
                         "thermal", "celsius", "°c", "heat", "burn"]),
    ("Road Damage",     ["subsid", "tarmac", "asphalt", "paving", "pavement",
                         "road surface", "road crack", "road damage", "cobblestone",
                         "footpath", "manhole", "crater"]),
]


def _keyword_in_text(keyword: str, text: str) -> bool:
    # Leading \b only — allows plurals and suffixes (e.g. "temperature" matches "temperatures")
    pattern = r"\b" + re.escape(keyword)
    return bool(re.search(pattern, text, re.IGNORECASE))


def _has_severity_keyword(description: str) -> bool:
    return any(_keyword_in_text(kw, description) for kw in SEVERITY_KEYWORDS)


def _match_category(description: str) -> tuple[str, list[str]]:
    """Return (category, matched_keywords). Falls back to Other if nothing matches."""
    for category, keywords in CATEGORY_RULES:
        hits = [kw for kw in keywords if _keyword_in_text(kw, description)]
        if hits:
            return category, hits
    return "Other", []


def _validate_and_fix(result: dict, description: str) -> dict:
    """Enforcement layer — applied unconditionally after every classification."""
    if result.get("category") not in CATEGORIES:
        result["category"] = "Other"
        result["flag"] = "NEEDS_REVIEW"

    # Severity keywords are authoritative over any other priority logic
    if _has_severity_keyword(description):
        result["priority"] = "Urgent"
    elif result.get("priority") not in ("Urgent", "Standard", "Low"):
        result["priority"] = "Standard"

    if not isinstance(result.get("reason"), str) or not result["reason"].strip():
        result["reason"] = "Description could not be matched to a specific category."

    if result.get("flag") not in ("NEEDS_REVIEW", ""):
        result["flag"] = ""

    return result


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row using keyword rules; always returns all four fields."""
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was empty or missing — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    priority = "Urgent" if _has_severity_keyword(description) else "Standard"
    category, matched = _match_category(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    if matched:
        quoted = ", ".join(f'"{kw}"' for kw in matched[:3])
        reason = f"Description contains {quoted}, indicating a {category} complaint."
    else:
        short = description[:80]
        reason = f"No category keywords matched in description: '{short}'."

    result = {"category": category, "priority": priority, "reason": reason, "flag": flag}
    return _validate_and_fix(result, description)


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write enriched results CSV."""
    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])
    except FileNotFoundError:
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: cannot parse input CSV '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(output_path, "w", encoding="utf-8"):
            pass
    except OSError as exc:
        print(f"ERROR: output path not writable '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    results = []
    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception as exc:
            classification = {
                "category": "Other",
                "priority": "Standard",
                "reason": f"Unexpected error during classification: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        results.append({**row, **classification})

    assert len(results) == len(rows), "Row count mismatch — output would differ from input"

    out_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
