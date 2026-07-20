"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and review flag.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# --- Classification Schema (from agents.md enforcement rules) ---

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword patterns — order matters (first match wins, more specific first)
CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole\w*\b", r"\bpot\s*hole\w*\b"],
    "Flooding": [r"\bflood\w*\b", r"\bwaterlogg\w*\b", r"\bsubmerg\w*\b", r"\bstrand\w*\b.*water", r"\bknee[\s-]*deep\b"],
    "Streetlight": [r"\bstreetlight\w*\b", r"\bstreet\s*light\w*\b", r"\blight\w*\s+out\b", r"\blights?\s+out\b", r"\bflicker\w*\b.*light", r"\blight\w*\s+flicker\w*\b", r"\bdark\b.*\blight\b", r"\bdark\w*\b.*\bnight\w*\b", r"\bspark\w*\b.*electr\w*", r"\belectr\w*\s+hazard\b", r"\bunlit\b", r"\bdarkness\b", r"\bsubstation\b.*\btrip\w*\b"],
    "Drain Blockage": [r"\bdrain\b.*\bblock\w*\b", r"\bblock\w*\b.*\bdrain\b", r"\bmanhole\b", r"\bsewer\b", r"\bclog\w*\b.*drain"],
    "Heritage Damage": [r"\bheritage\b", r"\bhistoric\w*\b.*damag\w*\b", r"\bmonument\b"],
    "Heat Hazard": [r"\bheat\b.*\bhazard\b", r"\bheatstroke\b", r"\bheat\s*wave\b", r"\bsunstroke\b", r"\bmelt\w*\b.*\b\d+\s*°?\s*[cC]\b", r"\b\d+\s*°?\s*[cC]\b.*\b(?:unbear|danger|burn|unsafe)\w*\b", r"\btemperatur\w*\b.*\b(?:danger|unbear|burn)\w*\b", r"\b(?:danger|unbear)\w*\b.*\btemperatur\w*\b", r"\bexpos\w*\b.*\bfull\s+sun\b", r"\bstor\w*\b.*\bheat\b", r"\bheat\b.*\bburn\w*\b", r"\bbubbl\w*\b.*\b\d+\s*°?\s*[cC]\b"],
    "Road Damage": [r"\broad\b.*\b(?:crack\w*|damag\w*|sink\w*|broken|cave|erode|collaps\w*|crater|subsid\w*|buckl\w*)\b", r"\b(?:crack\w*|damag\w*|sink\w*|cave|collaps\w*|crater|subsid\w*|buckl\w*)\b.*\broad\b", r"\bfootpath\b.*\b(?:broken|crack\w*|damag\w*|sink\w*)\b", r"\b(?:broken|crack\w*|sink\w*)\b.*\bfootpath\b", r"\btile\w*\s+broken\b", r"\bsurface\b.*\b(?:crack\w*|damag\w*|buckl\w*)\b", r"\bpav\w*\b.*\b(?:broken|remov\w*|upturn\w*)\b"],
    "Waste": [r"\bgarbage\b", r"\bwaste\b", r"\blitter\b", r"\btrash\b", r"\bdump\w*\b", r"\boverflow\w*\b.*\bbin\b", r"\bbin\w*\b.*\boverflow\w*\b", r"\bdead\s+animal\b", r"\brefuse\b", r"\bsmell\b.*\bgarbage\b", r"\bnot\s+clear\w*\b"],
    "Noise": [r"\bnoise\b", r"\bloud\b.*\bmusic\b", r"\bmusic\b.*\bmidnight\b", r"\bmusic\b.*\bnight\b", r"\bmusic\b.*\b\d+\s*[ap]m\b", r"\bhonk\w*\b", r"\bdisturb\w*\b.*\bsound\b", r"\bdrill\w*\b.*\b(?:daily|night|morning|residen)\w*\b", r"\bidling\b.*\bengine\b", r"\bamplifier\w*\b", r"\bband\b.*\b(?:play|night|11\s*pm)\w*\b"],
}


def _find_severity_keywords(description: str) -> list:
    """Find which severity keywords appear in the description."""
    desc_lower = description.lower()
    found = []
    for keyword in SEVERITY_KEYWORDS:
        # Use prefix match so "hospital" matches "hospitalised", "collapse" matches "collapsed"
        if re.search(r"\b" + re.escape(keyword) + r"\w*\b", desc_lower):
            found.append(keyword)
    return found


def _determine_category(description: str) -> tuple:
    """
    Determine the category from description text.
    Returns (category, matched_keywords, is_ambiguous).
    """
    desc_lower = description.lower()
    matched_categories = []

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                matched_categories.append(category)
                break  # One match per category is enough

    if len(matched_categories) == 0:
        return ("Other", [], True)
    elif len(matched_categories) == 1:
        return (matched_categories[0], matched_categories, False)
    else:
        # Multiple categories matched — pick the first (most specific) but flag as ambiguous
        return (matched_categories[0], matched_categories, True)


def _determine_priority(description: str, severity_hits: list) -> str:
    """
    Determine priority based on severity keywords.
    Urgent if any severity keyword is present, otherwise Standard.
    """
    if severity_hits:
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, severity_hits: list) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    # Extract a short quote from the description (first meaningful phrase)
    desc_trimmed = description.strip()
    # Take a representative snippet (up to 60 chars from description)
    snippet = desc_trimmed[:80].rstrip()
    if len(desc_trimmed) > 80:
        snippet = snippet.rsplit(" ", 1)[0] + "..."

    if severity_hits:
        keywords_str = ", ".join(f"'{k}'" for k in severity_hits)
        return f"Classified as {category} (Urgent) due to severity keywords [{keywords_str}] found in: \"{snippet}\""
    else:
        return f"Classified as {category} based on description: \"{snippet}\""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input: dict with keys including complaint_id and description.
    Output: dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement rules (from agents.md):
    - Category must be exactly one of the 10 allowed values.
    - Priority is Urgent if severity keywords are found in description.
    - Reason cites specific words from the description.
    - Flag is NEEDS_REVIEW when category is ambiguous or cannot be determined.
    - Empty/null descriptions → Other, Low, flagged NEEDS_REVIEW.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Error handling: empty, null, or non-string description
    if not description or not isinstance(description, str) or description.strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description insufficient for classification",
            "flag": "NEEDS_REVIEW"
        }

    description = description.strip()

    # Step 1: Determine category
    category, matched_cats, is_ambiguous = _determine_category(description)

    # Step 2: Check severity keywords for priority
    severity_hits = _find_severity_keywords(description)
    priority = _determine_priority(description, severity_hits)

    # Step 3: Build reason citing specific words
    reason = _build_reason(description, category, severity_hits)

    # Step 4: Set flag if ambiguous
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

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

    - Raises FileNotFoundError if input file doesn't exist.
    - Never crashes mid-batch: logs errors per row and continues.
    - Always produces output even if some rows fail.
    """
    # Validate input file exists
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise FileNotFoundError(f"Cannot read input file '{input_path}': {e}")

    results = []
    error_count = 0

    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            # Never crash mid-batch — log error and write fallback row
            error_count += 1
            complaint_id = row.get("complaint_id", f"ROW_{i}")
            print(f"WARNING: Row {i} ({complaint_id}) failed: {e}", file=sys.stderr)
            results.append({
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": "Row processing failed",
                "flag": "NEEDS_REVIEW"
            })

    # Write output CSV
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    if error_count > 0:
        print(f"WARNING: {error_count} row(s) failed classification. Check stderr for details.", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
