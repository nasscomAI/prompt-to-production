"""
UC-0A — Complaint Classifier
Rule-based civic complaint classifier built using the RICE → agents.md → skills.md → CRAFT workflow.
Classifies complaints into fixed taxonomy categories with severity-aware priority assignment.
"""
import argparse
import csv
import re
import sys


# ── Fixed Taxonomy (Enforcement Rule 1) ──────────────────────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# ── Severity Keywords (Enforcement Rule 2) ───────────────────────────────────
SEVERITY_KEYWORDS_PATTERNS = [
    (r"\binjur(?:y|ies|ed|ing)\b", "injury"),
    (r"\bchild(?:ren)?\b", "child"),
    (r"\bschools?\b", "school"),
    (r"\bhospital(?:s|ised|ized)?\b", "hospital"),
    (r"\bambulances?\b", "ambulance"),
    (r"\bfires?\b", "fire"),
    (r"\bhazards?\b", "hazard"),
    (r"\bfell\b|\bfall(?:ing|en)?\b", "fell"),
    (r"\bcollaps(?:e|ed|ing|es)\b", "collapse")
]

# ── Category Keyword Mapping ─────────────────────────────────────────────────
# Ordered by specificity — first match wins.
# Each entry: (category_name, list_of_patterns)
CATEGORY_RULES = [
    ("Pothole", [r"\bpotholes?\b"]),
    ("Flooding", [
        r"\bflood(?:ed|ing|s)?\b",
        r"\bwaterlog(?:ged|ging)?\b", r"\bsubmerg(?:e|ed|ing|es)?\b", r"\bknee[- ]?deep\b",
        r"\bwater\s*stagnation\b"
    ]),
    ("Drain Blockage", [
        r"\bdrains?\b.*\bblock(?:s|ed|ing)?\b", r"\bblock(?:s|ed|ing)?\b.*\bdrains?\b",
        r"\bchoked?\s*drains?\b", r"\bclog(?:ged|ging|s)?\b",
        r"\bdrains?\s*block(?:s|ed|ing)?\b"
    ]),
    ("Streetlight", [
        r"\bstreetlights?\b", r"\bstreet\s*lights?\b",
        r"\blights?\s*(?:out|off|tripped)\b", r"\bdark\s*at\s*night\b",
        r"\bflicker(?:ing|ed|s)?\b", r"\bspark(?:ing|ed|s)?\b",
        r"\bunlit\b", r"\bdarkness\b"
    ]),
    ("Heritage Damage", [r"\bheritage\b", r"\bhistoric(?:al)?\b", r"\bmonuments?\b", r"\bancient\b"]),
    ("Heat Hazard", [
        r"\bheat\s*hazard\b", r"\bheatwave\b", r"\bheat\s*stroke\b",
        r"\bheat\b", r"\bmelting\b", r"\btemperatures?\b", r"\bhot\b"
    ]),
    ("Noise", [
        r"\bnoise\b", r"\bloud\s*music\b", r"\bmusic\s*past\s*midnight\b",
        r"\bhonking\b", r"\bsound\s*pollution\b", r"\bplaying\s*music\b",
        r"\bplaying\b.*\bmusic\b", r"\baudible\b", r"\bwedding\s*band\b",
        r"\bamplifiers?\b"
    ]),
    ("Road Damage", [
        r"\broads?\b.*\bcrack(?:ed|ing)?\b", r"\bcrack(?:ed|ing|s)?\b", r"\bsink(?:ing|ed|s)?\b",
        r"\bsubsid(?:e|ed|ence|ing)?\b", r"\bbuckl(?:e|ed|ing)?\b",
        r"\bmanholes?\b.*\bmissing\b", r"\bmissing\b.*\bmanholes?\b",
        r"\bmanhole\s*covers?\b", r"\bfootpaths?\b.*\bbroken\b",
        r"\bbroken\b.*\bfootpaths?\b", r"\btiles?\s*broken\b",
        r"\bupturned\b", r"\broad\s*surfaces?\b.*\bdamage\b",
        r"\broad\s*damage\b", r"\bcrater\b"
    ]),
    ("Waste", [
        r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\brubbish\b",
        r"\bdump(?:ed|ing|s)?\b", r"\bdead\s*animals?\b", r"\blitter\b",
        r"\boverflow(?:ing|ed|s)?\b.*\bbins?\b", r"\bbins?\b.*\boverflow(?:ing|ed|s)?\b"
    ]),
]


def _match_category(description_lower: str) -> tuple:
    """
    Match description text against category rules.
    Returns (category, matched_keywords) or ("Other", []) if no match.
    """
    for category, patterns in CATEGORY_RULES:
        matched = []
        for pattern in patterns:
            if re.search(pattern, description_lower):
                matched.append(pattern)
        if matched:
            return category, matched
    return "Other", []


def _find_severity_hits(description_lower: str) -> list:
    """
    Find all severity keywords present in the description.
    Returns list of matched severity keywords.
    """
    hits = []
    for pattern, label in SEVERITY_KEYWORDS_PATTERNS:
        if re.search(pattern, description_lower):
            hits.append(label)
    return hits


def _build_reason(category: str, cat_keywords: list, severity_hits: list,
                  priority: str, description_lower: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    # Extract human-readable keyword snippets from the regex patterns
    cat_words = []
    for pat in cat_keywords:
        # Strip regex syntax to get readable text
        clean = re.sub(r"\\b|\\s[*+]|\[.*?\][?*+]?|\(\.\*\)|\(\.\+\)|\.\*|\.\+|\(\?:|\)|\+|\?|\^|\$", " ", pat).strip()
        clean = re.sub(r"\s+", " ", clean)
        if clean and clean not in cat_words:
            cat_words.append(clean)

    parts = []
    if cat_words:
        parts.append(f"Classified as {category} based on keywords: {', '.join(cat_words)}")
    else:
        parts.append(f"Classified as {category}")

    if severity_hits:
        parts.append(f"marked {priority} due to severity keywords: {', '.join(severity_hits)}")
    else:
        parts.append(f"priority {priority}")

    return "; ".join(parts) + "."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md):
      1. Category from fixed enum of 10 values only
      2. Urgent if severity keywords present
      3. Reason cites specific description words
      4. Ambiguous/empty → Other + NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle null/empty description (Enforcement Rule 4)
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower().strip()

    # Category detection (Enforcement Rule 1)
    category, cat_keywords = _match_category(desc_lower)

    # Severity / Priority detection (Enforcement Rule 2)
    severity_hits = _find_severity_hits(desc_lower)

    if severity_hits:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    # Flag ambiguous cases (Enforcement Rule 4)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    # Build reason (Enforcement Rule 3)
    reason = _build_reason(category, cat_keywords, severity_hits, priority, desc_lower)

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
    Handles bad rows gracefully — logs warning, continues processing.
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            for row_num, row in enumerate(reader, start=2):  # row 1 is header
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Never crash the batch (skills.md error_handling)
                    complaint_id = row.get("complaint_id", f"ROW_{row_num}")
                    print(f"WARNING: Error processing row {row_num} "
                          f"({complaint_id}): {e}", file=sys.stderr)
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error during classification: {e}",
                        "flag": "NEEDS_REVIEW"
                    })

    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
