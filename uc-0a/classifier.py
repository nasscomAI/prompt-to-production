"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md and skills.md.

Enforcement (from agents.md):
  - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
    Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - Priority must be Urgent if description contains any severity keyword
  - Every output row must include a reason citing specific words from the description
  - If category cannot be determined, output Other + NEEDS_REVIEW
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse", "burn", "unsafe",
]

CATEGORY_PATTERNS = [
    ("Pothole", [
        r"\bpothol\w*\b", r"\bpot\s*hol\w*\b", r"\bcrater\w*\b",
    ]),
    ("Flooding", [
        r"\bflood\w*\b", r"\bwaterlog\w*\b", r"\binundat\w*\b",
        r"\bknee[- ]deep\b", r"\bstranded\b",
        r"\bchannel\w*.*water\b", r"\bwater.*channel\w*\b",
        r"\brainwater\b",
    ]),
    ("Drain Blockage", [
        r"\bdrain\w*.*block\w*\b", r"\bblock\w*.*drain\w*\b",
        r"\bclog\w*.*drain\b", r"\bdrain\w*.*clog\w*\b",
        r"\bsewer\w*.*block\w*\b", r"\bblock\w*.*sewer\b",
        r"\bdrain\w*.*direct\w*\b",
    ]),
    ("Streetlight", [
        r"\bstreet\s*light\w*\b", r"\blight\w*.*out\b", r"\blight\w*.*flicker\w*\b",
        r"\blight\w*.*spark\w*\b", r"\b(?:lamp|pole).*out\b",
        r"\barea.*dark\b", r"\bdark.*area\b",
        r"\bunlit\b", r"\bwiring\s*theft\b",
        r"\bsubstation\b", r"\bdarkness\b",
    ]),
    ("Heritage Damage", [
        r"\bheritage\b",
        r"\bstep\s*well\b", r"\bmonument\b",
        r"\bhistoric\w*\b",
    ]),
    ("Heat Hazard", [
        r"\bheat\s*hazard\b", r"\bheat\s*wave\b", r"\bextreme\s*heat\b",
        r"\boverheat\w*\b",
        r"\bmelt\w*\b", r"\bbubbl\w*\b",
        r"\btemperature\w*\b",
        r"\bburn\w*\b", r"\bheatwave\b",
        r"\b\d{2}°[Cc]\b", r"\b\d{2}\s*degrees?\b",
    ]),
    ("Waste", [
        r"\bgarbage\b", r"\bwaste\b", r"\boverflow\w*.*bin\b", r"\bbin\w*.*overflow\w*\b",
        r"\brubbish\b", r"\blitter\b", r"\bdump\w*\b",
        r"\btrash\b", r"\bsmell\b", r"\bdead\s*animal\b",
    ]),
    ("Noise", [
        r"\bnoise\b", r"\bnoisy\b", r"\bmusic\b", r"\bloud\b",
        r"\bnoise\s*pollution\b", r"\bdisturbance\b",
        r"\bamplif\w*\b", r"\bband\b",
        r"\bdrill\w*\b", r"\bconstruction\b",
    ]),
    ("Road Damage", [
        r"\broad.*(?:damage|crack|broken|upturn|tile|subsidence|buckl\w*|sink\w*)\b",
        r"\b(?:damage|crack|broken|upturn|tile|subsidence|buckl\w*|sink\w*).*road\b",
        r"\bfootpath.*(?:broken|upturn|tile|damage|sink)\b",
        r"\b(?:broken|upturn|tile|damage|sink).*footpath\b",
        r"\bsurface.*(?:crack|sink|buckl)\b", r"\bsinking\b",
        r"\bpaving.*(?:broken|upturn|remov)\b", r"\b(?:broken|upturn|remov).*paving\b",
        r"\bcobblestone\w*\b",
    ]),
]


def _match_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return all keywords found in text (case-insensitive)."""
    found = []
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            found.append(kw)
    return found


def _detect_category(description: str) -> tuple[str, list[str]]:
    """
    Match description against category patterns.
    Returns (category, matched_keywords_for_reason).
    If multiple categories match, pick the first by priority order.
    If none match, returns (Other, []).
    """
    text_lower = description.lower()
    for category, patterns in CATEGORY_PATTERNS:
        for pat in patterns:
            match = re.search(pat, text_lower)
            if match:
                matched = [match.group(0).strip()]
                return category, matched
    return "Other", []


def _determine_priority(description: str) -> str:
    """Return Urgent if any severity keyword is present, else Standard."""
    found = _match_keywords(description, SEVERITY_KEYWORDS)
    return "Urgent" if found else "Standard"


def _build_reason(description: str, category: str, matched_keywords: list[str],
                  severity_hits: list[str]) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    parts = []
    if matched_keywords:
        quoted = ", ".join(f'"{w}"' for w in matched_keywords[:3])
        parts.append(f"Description contains {quoted} indicating {category}")
    if severity_hits:
        quoted = ", ".join(f'"{w}"' for w in severity_hits[:3])
        parts.append(f"Severity keywords found: {quoted}")
    if parts:
        return "; ".join(parts) + "."
    return f"Classified as {category} based on description content."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement (from agents.md):
      - Category must be exactly one of the allowed list
      - Priority must be Urgent if severity keywords present
      - Reason must cite specific words from the description
      - Ambiguous → Other + NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Error handling (from skills.md): empty description → Other + NEEDS_REVIEW
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description empty or unreadable.",
            "flag": "NEEDS_REVIEW",
        }

    # Detect category
    category, matched_keywords = _detect_category(description)

    # Determine priority
    severity_hits = _match_keywords(description, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity_hits else "Standard"

    # Build reason citing specific words
    reason = _build_reason(description, category, matched_keywords, severity_hits)

    # Flag if category is Other (ambiguous)
    flag = "NEEDS_REVIEW" if category == "Other" else ""

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

    Enforcement (from skills.md):
      - If input CSV cannot be read or is missing description column, halt and report
      - Do not produce partial output
    """
    # Validate input file
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print(f"ERROR: {input_path} is empty or has no header.", file=sys.stderr)
                sys.exit(1)
            if "description" not in reader.fieldnames:
                print(
                    f"ERROR: {input_path} is missing required 'description' column. "
                    f"Found columns: {reader.fieldnames}",
                    file=sys.stderr,
                )
                sys.exit(1)

            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Classify each row
    results = []
    for i, row in enumerate(rows):
        result = classify_complaint(row)
        results.append(result)

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Summary
    review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    print(f"Classified {len(results)} complaints: {urgent_count} Urgent, {review_count} NEEDS_REVIEW")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
