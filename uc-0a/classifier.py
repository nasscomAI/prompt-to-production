"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.
"""
import argparse
import csv
import sys
import re

# ---------------------------------------------------------------------------
# Classification schema (from README — must match exactly)
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

# Keyword → category mapping (order matters: more-specific first)
CATEGORY_RULES = [
    # Heritage
    (re.compile(r"\bheritage\b|\bmonument\b|\bhistoric\b", re.I), "Heritage Damage"),
    # Heat hazard
    (re.compile(r"\bheat\b|\bsun\b|\btemperature\b|\bheatwave\b", re.I), "Heat Hazard"),
    # Drain
    (re.compile(r"\bdrain\b|\bsewer\b|\bblockage\b|\bmanhole\b", re.I), "Drain Blockage"),
    # Flooding
    (re.compile(r"\bflood\b|\bflooded\b|\bflooding\b|\bfloods\b|\bsubmerg\b|\bwater.log\b|\bknee.deep\b|\bstranded\b", re.I), "Flooding"),
    # Pothole
    (re.compile(r"\bpothole\b|\bpit\b|\bcrater\b", re.I), "Pothole"),
    # Road damage (broader road surface issues)
    (re.compile(r"\broad\b.*\b(crack|sink|broke|broken|damage|uneven|rut)\b|\b(crack|sink|broke|broken|damage|uneven|rut)\b.*\broad\b|\bfootpath\b|\btile\b|\bpavement\b|\bsurface\b", re.I), "Road Damage"),
    # Streetlight
    (re.compile(r"\bstreetlights?\b|\blights?\s+out\b|\blampost\b|\belectric\b|\bspark\b", re.I), "Streetlight"),
    # Waste
    (re.compile(r"\bgarbage\b|\bwaste\b|\bbin\b|\blitter\b|\bdump\b|\banimal\b|\bdead\b", re.I), "Waste"),
    # Noise
    (re.compile(r"\bnoise\b|\bmusic\b|\bloud\b|\bsound\b|\bnight\b.*\b(music|play|party)\b", re.I), "Noise"),
]


def _determine_category(description: str) -> tuple[str, str]:
    """
    Return (category, flag).
    Tries each rule in order; first match wins.
    Falls back to Other + NEEDS_REVIEW if nothing matches.
    """
    for pattern, category in CATEGORY_RULES:
        if pattern.search(description):
            return category, ""
    return "Other", "NEEDS_REVIEW"


def _determine_priority(description: str) -> str:
    """
    Return 'Urgent' if any severity keyword appears in the description,
    'Standard' for clearly actionable issues, 'Low' otherwise.
    """
    desc_lower = description.lower()
    for keyword in SEVERITY_KEYWORDS:
        if keyword in desc_lower:
            return "Urgent"
    # Heuristic: complaints with a clear physical impact are Standard
    actionable_patterns = re.compile(
        r"\baffect\b|\bdamage\b|\bblock\b|\bstrand\b|\bflood\b|\bflooded\b|\bout\b|\bbreak\b"
        r"|\bcrack\b|\bmissing\b|\boverflow\b|\bsmell\b|\bsink\b|\bspark\b"
        r"|\bstranded\b|\bwater\b|\bcommuter\b|\bpothole\b|\bgarbage\b|\bdead\b",
        re.I
    )
    if actionable_patterns.search(description):
        return "Standard"
    return "Low"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Produce a one-sentence reason that quotes specific words from the description.
    Extracts the most diagnostic phrase (up to 10 words) from the description.
    """
    # Pick the first sentence or up to 12 words as the cited excerpt
    sentences = re.split(r'[.!?]', description.strip())
    excerpt = sentences[0].strip() if sentences else description.strip()
    # Truncate long excerpts to ~12 words
    words = excerpt.split()
    if len(words) > 12:
        excerpt = " ".join(words[:12]) + "..."
    return (
        f"Classified as {category} with {priority} priority "
        f"based on description: \"{excerpt}\"."
    )


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # --- Error case: empty description ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was empty or missing — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = _determine_category(description)
    priority = _determine_priority(description)
    reason = _build_reason(description, category, priority)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Rows that fail individually get a NEEDS_REVIEW entry rather than crashing.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not read input file: {exc}", file=sys.stderr)
        sys.exit(1)

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            cid = row.get("complaint_id", "UNKNOWN")
            print(f"WARNING: Unexpected error on {cid}: {exc}", file=sys.stderr)
            result = {
                "complaint_id": cid,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed due to unexpected error: {exc}",
                "flag": "NEEDS_REVIEW",
            }
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
