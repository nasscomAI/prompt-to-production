"""
UC-0A — Complaint Classifier

Classifies citizen complaints into structured categories with priority,
reason, and ambiguity flags based on the RICE enforcement rules defined
in agents.md.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv
import sys
import re


# --- Classification Schema ---

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword patterns mapped to categories (order matters — first match wins primary)
CATEGORY_PATTERNS = [
    ("Pothole", [r"\bpothole\b", r"\bpot\s*hole\b"]),
    ("Flooding", [r"\bflood\b", r"\bflooded\b", r"\bflooding\b", r"\bwaterlog\b", r"\bstranded\b", r"\bknee.?deep\b"]),
    ("Streetlight", [r"\bstreetlight\b", r"\bstreet\s*light\b", r"\blight[s]?\s+out\b", r"\blights?\s+not\s+working\b", r"\bflickering\b", r"\bdark\s+at\s+night\b"]),
    ("Drain Blockage", [r"\bdrain\b", r"\bmanhole\b", r"\bsewer\b", r"\bblocked\s+drain\b"]),
    ("Waste", [r"\bgarbage\b", r"\bwaste\b", r"\bdumped\b", r"\boverflowing\b.*\bbin\b", r"\bbin[s]?\b.*\boverflowing\b", r"\bdead\s+animal\b", r"\bnot\s+removed\b"]),
    ("Noise", [r"\bnoise\b", r"\bmusic\b.*\bmidnight\b", r"\bloud\b", r"\bmidnight\b.*\bmusic\b"]),
    ("Road Damage", [r"\broad\s*(surface|damage)\b", r"\bcracked\b", r"\bsinking\b", r"\bbroken\b.*\b(footpath|tile|pavement)\b", r"\btile[s]?\s+broken\b", r"\bupturned\b"]),
    ("Heritage Damage", [r"\bheritage\b"]),
    ("Heat Hazard", [r"\bheat\b", r"\bheatwave\b", r"\bhot\s+surface\b"]),
]


def _find_severity_keywords(description: str) -> list:
    """Find which severity keywords are present in the description."""
    desc_lower = description.lower()
    found = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower):
            found.append(kw)
    return found


def _match_categories(description: str) -> list:
    """Return list of matching categories ordered by match priority."""
    desc_lower = description.lower()
    matched = []
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                if category not in matched:
                    matched.append(category)
                break
    return matched


def _determine_priority(description: str, severity_hits: list) -> str:
    """Determine priority based on severity keywords and context."""
    if severity_hits:
        return "Urgent"

    # Standard: public inconvenience indicators
    standard_indicators = [
        r"\brisk\b", r"\bsafety\b", r"\bconcern\b", r"\baffect\b",
        r"\bstranded\b", r"\bdanger\b", r"\bblocked\b", r"\b\d+\s*days?\b"
    ]
    desc_lower = description.lower()
    for pattern in standard_indicators:
        if re.search(pattern, desc_lower):
            return "Standard"

    return "Standard"


def _build_reason(description: str, category: str, severity_hits: list) -> str:
    """Build a one-sentence reason citing words from the description."""
    # Extract key phrases from description for citation
    desc_words = description.strip()

    if severity_hits:
        kw_str = ", ".join(f"'{k}'" for k in severity_hits)
        return f"Classified as {category} (Urgent) due to severity keywords {kw_str} found in: \"{desc_words[:80]}...\""

    # Cite the first relevant portion of the description
    snippet = desc_words[:100]
    if len(desc_words) > 100:
        snippet += "..."
    return f"Classified as {category} based on description: \"{snippet}\""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle empty/null descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description insufficient for classification",
            "flag": "NEEDS_REVIEW"
        }

    # Find severity keywords
    severity_hits = _find_severity_keywords(description)

    # Match categories
    matched_categories = _match_categories(description)

    # Determine category
    if not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Multiple categories matched — ambiguous
        category = matched_categories[0]  # Best fit (first match by priority)
        flag = "NEEDS_REVIEW"

    # Determine priority
    priority = _determine_priority(description, severity_hits)

    # Build reason
    reason = _build_reason(description, category, severity_hits)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles bad rows gracefully — logs errors to stderr, writes output regardless.
    """
    results = []
    total = 0
    succeeded = 0
    failed = 0
    failed_rows = []

    # Read input
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Classify each row
    for i, row in enumerate(rows, start=1):
        total += 1
        try:
            result = classify_complaint(row)
            results.append(result)
            succeeded += 1
        except Exception as e:
            failed += 1
            cid = row.get("complaint_id", f"row-{i}")
            failed_rows.append((cid, str(e)))
            print(f"ERROR: Failed to classify {cid}: {e}", file=sys.stderr)

    # Write output
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}", file=sys.stderr)
        sys.exit(2)

    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total:     {total}")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed:    {failed}")
    print("=" * 60)

    if failed_rows:
        print("  Failed rows:")
        for cid, err in failed_rows:
            print(f"    - {cid} ({err})")
        sys.exit(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
