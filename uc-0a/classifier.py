"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Role: Citizen Complaint Classifier for municipal civic grievance system.
Intent: Classify each complaint into category + priority + reason + flag.
Context: Uses only the complaint description text; no external knowledge.
Enforcement: Strict allowed values, severity keyword triggers, reason citing, ambiguity flagging.
"""
import argparse
import csv
import re
import sys

# ── Classification Schema (from README) ──────────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# ── Keyword → Category mapping ───────────────────────────────────────────────
# Order matters: more specific patterns checked first to avoid mis-classification.

CATEGORY_RULES = [
    # (keywords_list, category)
    (["pothole", "pot hole", "pot-hole"], "Pothole"),
    (["flood", "flooded", "flooding", "waterlog", "water-log", "submerge", "knee-deep", "waist-deep"], "Flooding"),
    (["streetlight", "street light", "street-light", "lamp post", "lamppost", "lights out", "light out", "flickering", "sparking"], "Streetlight"),
    (["garbage", "waste", "trash", "rubbish", "litter", "dumped", "dump", "overflowing", "dead animal", "bins"], "Waste"),
    (["noise", "loud", "music", "honking", "blaring", "midnight", "decibel"], "Noise"),
    (["heritage", "monument", "historical", "old city", "heritage street"], "Heritage Damage"),
    (["heat", "temperature", "heatwave", "sunstroke", "heat stroke", "hot surface"], "Heat Hazard"),
    (["drain", "drainage", "gutter", "sewer", "manhole", "nala", "nallah"], "Drain Blockage"),
    (["road damage", "road surface", "cracked", "sinking", "crack", "broken road",
      "broken footpath", "footpath", "tiles broken", "upturned", "uneven road"], "Road Damage"),
]


def _match_category(description_lower: str) -> tuple[str, bool]:
    """
    Match a description to a category using keyword rules.
    Returns (category, is_ambiguous).
    """
    matches = []
    for keywords, category in CATEGORY_RULES:
        for kw in keywords:
            if kw in description_lower:
                if category not in matches:
                    matches.append(category)
                break  # one keyword hit per rule is enough

    if len(matches) == 1:
        return matches[0], False
    elif len(matches) > 1:
        # Multiple categories matched — pick the first (most specific) but flag
        return matches[0], True
    else:
        return "Other", True


def _check_severity(description_lower: str) -> tuple[str, list[str]]:
    """
    Check for severity keywords. Returns (priority, matched_keywords).
    """
    matched = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]
    if matched:
        return "Urgent", matched
    return "Standard", []


def _build_reason(category: str, priority: str, description: str,
                  severity_hits: list[str], description_lower: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description.
    """
    # Find the strongest evidence snippet (first matching keyword from description)
    evidence_words = []

    # Gather category evidence
    for keywords, cat in CATEGORY_RULES:
        if cat == category:
            for kw in keywords:
                if kw in description_lower:
                    evidence_words.append(f'"{kw}"')
            break

    # Gather severity evidence
    for kw in severity_hits:
        evidence_words.append(f'"{kw}"')

    if evidence_words:
        evidence_str = ", ".join(evidence_words[:3])  # limit to 3 for conciseness
        return (f"Classified as {category}/{priority} because description contains "
                f"{evidence_str}.")
    else:
        return (f"Classified as {category}/{priority} based on overall description context.")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Implements RICE enforcement:
      E1: Category from allowed list only
      E2: Urgent if severity keywords present
      E3: Reason cites specific description words
      E4: NEEDS_REVIEW on ambiguity
      E5: Preserves complaint_id
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty / missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }

    description_lower = description.lower()

    # Step 1 — Category matching (E1)
    category, is_ambiguous = _match_category(description_lower)

    # Step 2 — Priority via severity keywords (E2)
    priority, severity_hits = _check_severity(description_lower)

    # If not urgent, gauge between Standard and Low
    if priority != "Urgent":
        days_open = int(row.get("days_open", 0)) if row.get("days_open", "").strip().isdigit() else 0
        priority = "Standard" if days_open >= 7 else "Low" if days_open <= 2 else "Standard"

    # Step 3 — Reason citing description words (E3)
    reason = _build_reason(category, priority, description, severity_hits, description_lower)

    # Step 4 — Ambiguity flag (E4)
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

    Enforcement:
      - Flags nulls / bad rows instead of crashing
      - Produces output even if some rows fail
      - Preserves row order; no duplicates or drops
    """
    results = []
    errors = []

    # Read input CSV
    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("WARNING: Input CSV has no data rows.", file=sys.stderr)

    # Classify each row
    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            errors.append(f"Row {i + 1} ({row.get('complaint_id', '?')}): {e}")
            results.append({
                "complaint_id": row.get("complaint_id", f"ROW_{i + 1}"),
                "category": "Other",
                "priority": "Low",
                "reason": "Classification failed — manual review required.",
                "flag": "NEEDS_REVIEW"
            })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Report
    print(f"Processed {len(results)} complaints ({len(errors)} errors).")
    if errors:
        for err in errors:
            print(f"  ⚠ {err}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
