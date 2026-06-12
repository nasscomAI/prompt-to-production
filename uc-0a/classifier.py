"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and review flag.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# ── Allowed values (from agents.md enforcement) ──────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that force priority → Urgent (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# ── Category keyword mappings ─────────────────────────────────────────────────
# Order matters: more specific patterns are checked first.
# Each entry: (category_name, list_of_keyword_patterns, list_of_negative_patterns)

CATEGORY_RULES = [
    (
        "Pothole",
        [r"\bpothole\b", r"\bpot\s*hole\b"],
        []
    ),
    (
        "Flooding",
        [r"\bflood\w*\b", r"\bwaterlogg\w*\b", r"\bsubmerg\w*\b",
         r"\bstranded\b", r"\bknee[\s-]*deep\b", r"\binundat\w*\b",
         r"\bstanding\s+in\s+water\b"],
        []
    ),
    (
        "Drain Blockage",
        [r"\bdrain\w*\b", r"\bmanhole\b", r"\bsewer\w*\b",
         r"\bblocked\s+drain\b", r"\bclogged\b", r"\bnala\b"],
        []
    ),
    (
        "Streetlight",
        [r"\bstreetlight\w*\b", r"\bstreet\s*light\w*\b",
         r"\blight\w*\s+out\b", r"\blamp\s*post\b", r"\bflicker\w*\b",
         r"\bdark\s+at\s+night\b", r"\blights?\s+out\b",
         r"\bspark\w*\b"],
        []
    ),
    (
        "Noise",
        [r"\bnois\w*\b", r"\bmusic\b", r"\bloud\b", r"\bdecibel\b",
         r"\bmidnight\b", r"\bblaring\b", r"\bhorn\w*\b"],
        []
    ),
    (
        "Waste",
        [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\bdump\w*\b",
         r"\blitter\w*\b", r"\bdead\s+animal\b", r"\boverflow\w*\b",
         r"\brefuse\b", r"\bbin\w?\b", r"\brubbish\b"],
        []
    ),
    (
        "Heritage Damage",
        [r"\bheritage\b", r"\bhistoric\w*\b", r"\bmonument\b",
         r"\bancient\b", r"\barchaeolog\w*\b"],
        []
    ),
    (
        "Heat Hazard",
        [r"\bheat\b", r"\bheatwave\b", r"\bheat\s*stroke\b",
         r"\bsunstroke\b", r"\btemperature\b"],
        []
    ),
    (
        "Road Damage",
        [r"\broad\s+(?:damage|crack|sinking|cave|broken|deteriorat)\w*\b",
         r"\bcrack\w*\b", r"\bsinking\b", r"\bcave[\s-]*in\b",
         r"\bfootpath\b", r"\btile\w*\s+broken\b", r"\bupturned\b",
         r"\bsurface\s+(?:crack|damag)\w*\b"],
        # Exclude if it's clearly a pothole
        [r"\bpothole\b"]
    ),
]


def _find_severity_keywords(description: str) -> list[str]:
    """Return list of severity keywords found in the description."""
    desc_lower = description.lower()
    found = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", desc_lower):
            found.append(kw)
    return found


def _match_category(description: str) -> tuple[str, list[str]]:
    """
    Match description against category rules.
    Returns (category, list_of_matched_keywords).
    """
    desc_lower = description.lower()
    matches: list[tuple[str, list[str]]] = []

    for category, patterns, negatives in CATEGORY_RULES:
        # Skip if negative patterns match
        if any(re.search(neg, desc_lower) for neg in negatives):
            continue

        matched_words = []
        for pattern in patterns:
            found = re.findall(pattern, desc_lower)
            matched_words.extend(found)

        if matched_words:
            matches.append((category, matched_words))

    if not matches:
        return "Other", []

    # Return the first (highest-priority) match
    return matches[0][0], matches[0][1]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules from agents.md:
    - Category must be one of 10 allowed values
    - Priority = Urgent if severity keywords found
    - Reason must cite specific words from description
    - Flag = NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle missing/empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # ── Step 1: Determine category ────────────────────────────────────────
    category, matched_keywords = _match_category(description)

    # ── Step 2: Determine priority ────────────────────────────────────────
    severity_hits = _find_severity_keywords(description)
    if severity_hits:
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # ── Step 3: Set flag ──────────────────────────────────────────────────
    flag = ""
    if category == "Other" and matched_keywords == []:
        flag = "NEEDS_REVIEW"

    # ── Step 4: Build reason citing specific words ────────────────────────
    reason_parts = []
    if matched_keywords:
        unique_keywords = list(dict.fromkeys(matched_keywords))  # dedupe, preserve order
        reason_parts.append(
            f"Classified as {category} based on keywords: {', '.join(unique_keywords)}"
        )
    else:
        reason_parts.append(
            f"Classified as {category} — no specific category keywords matched in description"
        )

    if severity_hits:
        reason_parts.append(
            f"priority set to Urgent due to severity keywords: {', '.join(severity_hits)}"
        )

    reason = "; ".join(reason_parts) + "."

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
    Handles errors gracefully — never crashes, always produces output.
    """
    results = []
    errors = 0
    total = 0

    try:
        with open(input_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    errors += 1
                    complaint_id = row.get("complaint_id", f"ROW-{total}")
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    print(f"  ⚠ Row {total} ({complaint_id}): {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    # Summary
    print(f"  Processed: {total} rows")
    print(f"  Successful: {total - errors}")
    if errors:
        print(f"  Errors (fallback applied): {errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
