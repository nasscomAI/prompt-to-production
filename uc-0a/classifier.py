"""
UC-0A — Complaint Classifier
Deterministic rule-based classifier built using RICE → agents.md → skills.md → CRAFT workflow.
Uses keyword matching against the fixed category enum and severity keyword list.
"""
import argparse
import csv
import re
import sys


# --- Enforcement: Exact allowed values from agents.md ---

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# --- Category keyword mapping ---
# Each category maps to keywords/phrases likely found in complaint descriptions.
# Order matters: more specific patterns checked first to avoid misclassification.

CATEGORY_RULES = [
    ("Heritage Damage", [
        r"\bheritage\b", r"\bhistoric\b", r"\bmonument\b", r"\barchaeolog"
    ]),
    ("Heat Hazard", [
        r"\bheat\s*(wave|stroke|hazard)\b", r"\bextreme\s*heat\b",
        r"\bsunstroke\b", r"\bheatstroke\b"
    ]),
    ("Drain Blockage", [
        r"\bdrain\b.*\bblock", r"\bblock.*\bdrain\b",
        r"\bclogged\s*drain\b", r"\bchoked\s*drain\b",
        r"\bdrainage\s*(block|clog|choke)"
    ]),
    ("Flooding", [
        r"\bflood", r"\bwaterlogg", r"\bwater\s*logg",
        r"\bsubmerg", r"\binundat", r"\bknee[\s-]*deep\b",
        r"\bstanding\s*(in\s*)?water\b", r"\bwater\s*stagnati"
    ]),
    ("Pothole", [
        r"\bpothole\b", r"\bpot[\s-]*hole\b"
    ]),
    ("Streetlight", [
        r"\bstreetlight\b", r"\bstreet\s*light\b", r"\blight[s]?\s*out\b",
        r"\blight[s]?\s*not\s*work", r"\bflicker", r"\bspark",
        r"\blamp\s*post\b", r"\bdark\s*(at\s*night|area|street)\b",
        r"\blights?\s*out\b"
    ]),
    ("Noise", [
        r"\bnoise\b", r"\bloud\b", r"\bmusic\b.*\b(midnight|night|late)\b",
        r"\b(midnight|night|late)\b.*\bmusic\b", r"\bdecibel\b",
        r"\bnuisance\s*sound\b", r"\bhonk"
    ]),
    ("Waste", [
        r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\brubbish\b",
        r"\bdump", r"\boverflow.*\bbin", r"\bbin.*\boverflow",
        r"\blitter", r"\bdead\s*animal\b", r"\brefuse\b", r"\bdebris\b",
        r"\bsmell\b", r"\bstink\b", r"\bstench\b"
    ]),
    ("Road Damage", [
        r"\broad\s*(surface|crack|damag|sinking|cave)", r"\bcave[\s-]*in\b",
        r"\bsinking\b", r"\bcrack", r"\bfootpath\b.*\b(broken|damage|crack|upturn)",
        r"\b(broken|damage|crack|upturn).*\bfootpath\b",
        r"\bmanhole\b", r"\btile[s]?\s*(broken|upturn|crack|damag)",
        r"\bpavement\b.*\b(broken|damage|crack)"
    ]),
]


def _detect_category(description: str) -> tuple:
    """
    Detect the best-fit category from the description using keyword rules.
    Returns (category, is_ambiguous, matched_keywords).
    """
    desc_lower = description.lower()
    matches = []

    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                matches.append(category)
                break  # One match per category is enough

    if not matches:
        return ("Other", True, [])
    elif len(matches) == 1:
        return (matches[0], False, matches)
    else:
        # Multiple categories matched — use the first (highest priority) but flag
        # Check if truly ambiguous (different categories matched)
        unique = list(dict.fromkeys(matches))
        if len(unique) == 1:
            return (unique[0], False, unique)
        else:
            return (unique[0], True, unique)


def _detect_severity(description: str) -> tuple:
    """
    Check if any severity keywords are present in the description.
    Returns (is_urgent, list_of_matched_keywords).
    """
    desc_lower = description.lower()
    found = []
    for keyword in SEVERITY_KEYWORDS:
        # Use word boundary matching to avoid partial matches
        if re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower):
            found.append(keyword)
    return (len(found) > 0, found)


def _build_reason(description: str, category: str, severity_keywords: list) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    # Extract a key phrase from the description to cite
    desc_lower = description.lower()

    # Find a representative snippet to cite (first ~8 significant words)
    words = description.split()
    if len(words) > 10:
        snippet = " ".join(words[:8]) + "..."
    else:
        snippet = description

    if severity_keywords:
        kw_str = ", ".join(severity_keywords)
        return (f'Classified as {category} based on description mentioning '
                f'"{snippet}"; marked Urgent due to severity keyword(s): {kw_str}.')
    else:
        return (f'Classified as {category} based on description mentioning '
                f'"{snippet}".')


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Implements the enforcement rules from agents.md:
    1. Category from exact enum of 10 values
    2. Priority from exact enum (Urgent/Standard/Low)
    3. Severity keywords force Urgent
    4. Reason cites complaint description
    5. NEEDS_REVIEW for genuine ambiguity
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    # Step 1: Detect category
    category, is_ambiguous, matched_categories = _detect_category(description)

    # Step 2: Detect severity
    is_urgent, severity_keywords = _detect_severity(description)

    # Step 3: Determine priority
    if is_urgent:
        priority = "Urgent"
    elif category in ("Flooding", "Road Damage", "Drain Blockage"):
        # Higher-impact infrastructure categories default to Standard
        priority = "Standard"
    else:
        priority = "Standard"

    # Step 4: Build reason
    reason = _build_reason(description, category, severity_keywords)

    # Step 5: Set flag
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    # Validate category is in allowed list (defensive check)
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Validate priority is in allowed list (defensive check)
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

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
    Never crashes mid-batch — always produces a complete output file.
    Reports failed rows to stderr.
    """
    results = []
    failed_count = 0

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row_num, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                failed_count += 1
                print(f"WARNING: Row {row_num} failed: {e}", file=sys.stderr)
                results.append({
                    "complaint_id": row.get("complaint_id", f"UNKNOWN-{row_num}"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed for this row.",
                    "flag": "NEEDS_REVIEW"
                })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed {len(results)} complaints. Written to {output_path}")
    if failed_count:
        print(f"WARNING: {failed_count} rows failed classification.", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
