"""
UC-0A — Complaint Classifier
Implements the RICE enforcement rules from agents.md and the two skills from skills.md.
"""
import argparse
import csv
import re
import sys

# ── Classification Schema (from agents.md enforcement rules) ──────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# ── Category keyword mapping ─────────────────────────────────────────────────
# Each category maps to a list of keyword patterns checked against the description.
# Order matters: more specific categories are checked first to avoid mis-classification.

CATEGORY_PATTERNS = {
    "Heritage Damage": [
        r"heritage", r"monument", r"historical", r"ancient", r"archaeological",
        r"heritage\s+street", r"old\s+city"
    ],
    "Heat Hazard": [
        r"heat\s*stroke", r"heat\s*wave", r"extreme\s*heat",
        r"heat\s*hazard", r"sun\s*stroke", r"temperature"
    ],
    "Drain Blockage": [
        r"drain\s*block", r"blocked\s*drain", r"clogged\s*drain",
        r"drain\s*overflow", r"manhole", r"sewage", r"sewer"
    ],
    "Flooding": [
        r"flood", r"waterlog", r"water\s*log", r"submerge",
        r"knee[\s-]*deep", r"water\s*stagnat", r"inundat",
        r"stranded", r"inaccessible"
    ],
    "Pothole": [
        r"pothole", r"pot\s*hole", r"crater", r"tyre\s*damage",
        r"tire\s*damage"
    ],
    "Road Damage": [
        r"road\s*damage", r"road\s*surface\s*crack", r"road\s*crack",
        r"sinking", r"broken\s*road", r"footpath.*broken",
        r"broken.*footpath", r"tiles?\s*broken", r"upturned",
        r"road\s*cave", r"asphalt"
    ],
    "Streetlight": [
        r"streetlight", r"street\s*light", r"light.*out",
        r"lamp\s*post", r"dark\s*at\s*night", r"no\s*light",
        r"flickering", r"sparking", r"lights?\s*out"
    ],
    "Waste": [
        r"garbage", r"waste", r"trash", r"rubbish", r"litter",
        r"dumped", r"dump", r"overflowing.*bin", r"dead\s*animal",
        r"not\s*removed", r"debris", r"bulk\s*waste"
    ],
    "Noise": [
        r"noise", r"loud", r"music.*midnight", r"midnight.*music",
        r"decibel", r"horn", r"blaring", r"sound\s*pollution",
        r"noise\s*pollution", r"past\s*midnight"
    ],
}


def _match_category(description: str) -> tuple[str, list[str], bool]:
    """
    Match description to a category using keyword patterns.
    Returns (category, matched_keywords, is_ambiguous).
    """
    desc_lower = description.lower()
    matches = {}  # category -> list of matched keywords

    for category, patterns in CATEGORY_PATTERNS.items():
        matched = []
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                matched.append(re.search(pattern, desc_lower).group())
        if matched:
            matches[category] = matched

    if not matches:
        return "Other", [], True

    if len(matches) == 1:
        cat = list(matches.keys())[0]
        return cat, matches[cat], False

    # Multiple category matches — pick the one with the most keyword hits
    ranked = sorted(matches.items(), key=lambda x: len(x[1]), reverse=True)
    best_cat, best_kw = ranked[0]
    second_cat, second_kw = ranked[1]

    # Ambiguous if top two have equal number of keyword matches
    is_ambiguous = len(best_kw) == len(second_kw)

    return best_cat, best_kw, is_ambiguous


def _check_severity(description: str) -> tuple[bool, list[str]]:
    """
    Check if description contains any severity keywords that trigger Urgent priority.
    Returns (is_urgent, matched_severity_keywords).
    """
    desc_lower = description.lower()
    matched = [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + kw + r'\b', desc_lower)]
    return bool(matched), matched


def _determine_priority(is_urgent: bool, description: str) -> str:
    """Determine priority: Urgent if severity keywords present, else Standard or Low."""
    if is_urgent:
        return "Urgent"

    # Heuristic: Standard for most complaints; Low for minor/cosmetic issues
    desc_lower = description.lower()
    low_indicators = [
        r"minor", r"cosmetic", r"small", r"slight", r"trivial",
        r"not\s*urgent", r"low\s*priority", r"inconvenience"
    ]
    for pattern in low_indicators:
        if re.search(pattern, desc_lower):
            return "Low"

    return "Standard"


def _build_reason(category: str, priority: str, cat_keywords: list[str],
                  severity_keywords: list[str]) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    parts = []
    if cat_keywords:
        parts.append(f"description mentions {', '.join(repr(k) for k in cat_keywords[:3])}")
    if severity_keywords:
        parts.append(f"severity keyword(s) {', '.join(repr(k) for k in severity_keywords)} trigger Urgent priority")

    if parts:
        return f"Classified as {category} ({priority}) because {'; '.join(parts)}."
    return f"Classified as {category} ({priority}) based on overall description content."


# ── Skill 1: classify_complaint ───────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Implements the classify_complaint skill from skills.md and
    enforcement rules from agents.md.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # Error handling: empty or missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description not classifiable.",
            "flag": "NEEDS_REVIEW"
        }

    # Step 1: Match category
    category, cat_keywords, is_ambiguous = _match_category(description)

    # Step 2: Check severity keywords for priority
    is_urgent, severity_keywords = _check_severity(description)
    priority = _determine_priority(is_urgent, description)

    # Step 3: Build reason citing specific words
    reason = _build_reason(category, priority, cat_keywords, severity_keywords)

    # Step 4: Set flag if ambiguous
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


# ── Skill 2: batch_classify ──────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Implements the batch_classify skill from skills.md:
    - Reads test_[city].csv
    - Applies classify_complaint per row
    - Writes all original columns + category, priority, reason, flag
    - Logs warnings for failed rows but continues processing
    """
    # Error handling: file not found
    try:
        infile = open(input_path, "r", newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot read input file: {e}", file=sys.stderr)
        sys.exit(1)

    reader = csv.DictReader(infile)
    input_fieldnames = reader.fieldnames or []
    output_fieldnames = list(input_fieldnames) + ["category", "priority", "reason", "flag"]

    results = []
    for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
        try:
            classification = classify_complaint(row)
            out_row = dict(row)
            out_row["category"] = classification["category"]
            out_row["priority"] = classification["priority"]
            out_row["reason"] = classification["reason"]
            out_row["flag"] = classification["flag"]
            results.append(out_row)
        except Exception as e:
            print(f"WARNING: Row {row_num} (complaint_id={row.get('complaint_id', '?')}) "
                  f"failed classification: {e}", file=sys.stderr)
            out_row = dict(row)
            out_row["category"] = "Other"
            out_row["priority"] = "Low"
            out_row["reason"] = "Classification failed."
            out_row["flag"] = "NEEDS_REVIEW"
            results.append(out_row)

    infile.close()

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
