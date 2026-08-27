"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify skills as defined in
agents.md (RICE enforcement) and skills.md (I/O contracts).
"""
import argparse
import csv
import re
import sys


# ---------------------------------------------------------------------------
# Classification schema (from UC-0A README and agents.md enforcement rules)
# ---------------------------------------------------------------------------

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

# Severity keywords that MUST trigger priority = "Urgent"
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping (ordered: more-specific patterns first)
CATEGORY_RULES = [
    # Heritage Damage — must come before Road Damage / Streetlight
    (["heritage", "historic", "monument", "old city"], "Heritage Damage"),

    # Drain Blockage
    (["drain blocked", "drain blockage", "blocked drain", "drain clogged",
      "drain overflow", "sewer block", "drainage block"], "Drain Blockage"),

    # Flooding
    (["flood", "flooded", "waterlogged", "water logging", "submerged",
      "standing water", "knee-deep", "inundated"], "Flooding"),

    # Pothole
    (["pothole", "pot hole", "pot-hole", "tyre damage", "wheel damage"], "Pothole"),

    # Streetlight / lighting
    (["streetlight", "street light", "lamp", "lighting", "lights out",
      "light out", "flickering", "sparking", "dark at night",
      "no light", "electrical"], "Streetlight"),

    # Waste / garbage
    (["garbage", "waste", "rubbish", "trash", "litter", "overflowing bin",
      "dustbin", "dead animal", "carcass", "rotting"], "Waste"),

    # Noise
    (["noise", "music", "loud", "sound", "midnight", "late night music",
      "blaring"], "Noise"),

    # Heat Hazard
    (["heat", "temperature", "sunstroke", "heat stroke", "hot"], "Heat Hazard"),

    # Road Damage (broader road surface issues — after pothole/flooding)
    (["road surface", "cracked road", "sinking", "broken road",
      "road damage", "road crack", "footpath", "tiles broken",
      "manhole", "missing cover", "road collapsed", "road repair",
      "utility work", "tarmac", "pavement"], "Road Damage"),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Return (category, is_ambiguous) based on description text.
    Enforces agents.md rule: use only description, exact category strings.
    """
    lower = description.lower()
    matched = []

    for keywords, category in CATEGORY_RULES:
        for kw in keywords:
            if kw in lower:
                matched.append(category)
                break  # one match per rule is enough

    # Deduplicate while preserving order
    seen = set()
    unique_matched = []
    for cat in matched:
        if cat not in seen:
            seen.add(cat)
            unique_matched.append(cat)

    if len(unique_matched) == 1:
        return unique_matched[0], False
    elif len(unique_matched) == 0:
        return "Other", True          # cannot determine → NEEDS_REVIEW
    else:
        # Multiple categories matched → pick first (highest priority rule)
        # and flag for review only if they are genuinely different types
        return unique_matched[0], True


def _detect_priority(description: str) -> str:
    """
    Enforce agents.md rule: Urgent if any severity keyword is present.
    """
    lower = description.lower()
    for kw in URGENT_KEYWORDS:
        # Word-boundary match to avoid false positives (e.g. 'fire' in 'firefighter')
        if re.search(r'\b' + re.escape(kw) + r'\b', lower):
            return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str) -> str:
    """
    Craft one sentence that cites specific words from the description.
    Enforces agents.md rule: reason must reference description text.
    """
    # Trim description to a representative excerpt (≤120 chars) for the reason
    excerpt = description.strip()
    if len(excerpt) > 120:
        excerpt = excerpt[:117].rstrip() + "..."
    return f"Classified as {category} based on complaint: \"{excerpt}\"."


# ---------------------------------------------------------------------------
# Public skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Input : dict with keys from the test CSV (description is the key field).
    Output: dict — complaint_id, category, priority, reason, flag.

    Enforces all agents.md rules:
    - Exact category strings only.
    - Urgent triggered by severity keywords.
    - Reason cites description text.
    - NEEDS_REVIEW set when category cannot be determined.
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # Guard: empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)
    reason = _build_reason(description, category)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Public skill: batch_classify
# ---------------------------------------------------------------------------

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Skill: batch_classify
    Reads input CSV, applies classify_complaint per row, writes results CSV.

    Resilience (from skills.md error_handling):
    - Skips rows that raise unexpected exceptions (logs warning to stderr).
    - Always writes the output file even if some rows fail.
    - Inserts NEEDS_REVIEW flag for failed rows.
    """
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                except Exception as exc:  # pylint: disable=broad-except
                    complaint_id = row.get("complaint_id", f"ROW-{i}")
                    print(
                        f"[WARN] Row {i} ({complaint_id}) failed: {exc}",
                        file=sys.stderr,
                    )
                    result = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {exc}",
                        "flag": "NEEDS_REVIEW",
                    }
                results.append(result)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"[INFO] Classified {len(results)} complaint(s).", file=sys.stderr)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
