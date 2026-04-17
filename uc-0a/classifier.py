"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify skills defined in skills.md.
Agent role, intent, context, and enforcement rules are sourced from agents.md.
"""
import argparse
import csv
import sys

# ---------------------------------------------------------------------------
# Enforcement constants (from agents.md → context + enforcement)
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

OUTPUT_FIELDNAMES = ["complaint_id", "category", "priority", "reason", "flag"]


# ---------------------------------------------------------------------------
# Skill: classify_complaint
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint row.

    Enforcement rules (agents.md):
      1. category MUST exactly match one of ALLOWED_CATEGORIES.
      2. priority MUST be 'Urgent' if any SEVERITY_KEYWORDS appear in description.
      3. reason MUST be one sentence citing specific words from the description.
      4. If category is genuinely ambiguous, set flag to 'NEEDS_REVIEW'.

    Args:
        row: dict with at least 'complaint_id' and 'description' keys.

    Returns:
        dict with keys: complaint_id, category, priority, reason, flag.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Rule 1 + 4: Determine category from description keywords ---
    category, flag = _infer_category(desc_lower)

    # --- Rule 2: Determine priority via severity keyword scan ---
    triggered_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if triggered_keywords else "Standard"

    # --- Rule 3: Build a one-sentence reason citing source words ---
    reason = _build_reason(description, category, priority, triggered_keywords, flag)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _infer_category(desc_lower: str) -> tuple[str, str]:
    """
    Map description text to an allowed category.
    Returns (category, flag) where flag is 'NEEDS_REVIEW' if ambiguous.
    """
    # Keyword → category mapping (ordered: most specific first)
    keyword_map = [
        (["pothole", "pot hole", "pit in road"],          "Pothole"),
        (["flood", "waterlogging", "waterlogged",
          "water logging", "submerged"],                  "Flooding"),
        (["streetlight", "street light", "lamp post",
          "light post", "no light", "dark road"],         "Streetlight"),
        (["garbage", "waste", "trash", "litter",
          "dumping", "sanitation", "rubbish"],             "Waste"),
        (["noise", "loud", "sound", "disturbance",
          "honking"],                                      "Noise"),
        (["road damage", "road broken", "damaged road",
          "crack", "cracked road", "road cracked"],        "Road Damage"),
        (["heritage", "monument", "historical",
          "ancient"],                                      "Heritage Damage"),
        (["heat", "temperature", "hot pavement",
          "heat hazard"],                                  "Heat Hazard"),
        (["drain", "drainage", "sewer", "blocked drain",
          "drain block"],                                  "Drain Blockage"),
    ]

    matches = []
    for keywords, category in keyword_map:
        if any(kw in desc_lower for kw in keywords):
            matches.append(category)

    if len(matches) == 1:
        return matches[0], ""
    elif len(matches) > 1:
        # Ambiguous: multiple categories match → flag for review, pick first
        return matches[0], "NEEDS_REVIEW"
    else:
        # No match → Other + flag for review
        return "Other", "NEEDS_REVIEW"


def _build_reason(description: str, category: str, priority: str,
                  triggered_keywords: list[str], flag: str) -> str:
    """
    Build a one-sentence reason that cites specific words from the description.
    """
    # Find the first matching source word visible in original description
    desc_lower = description.lower()

    if triggered_keywords:
        cited = f"'{triggered_keywords[0]}'"
        urgency_note = f" and severity keyword {cited} indicates Urgent priority"
    else:
        urgency_note = ""

    # Cite a word from description that drove the category
    category_kw = _find_category_keyword(desc_lower, category)
    cited_cat = f"'{category_kw}'" if category_kw else "the description"

    if flag == "NEEDS_REVIEW":
        return (
            f"Classified as {category} based on {cited_cat} in the description"
            f"{urgency_note}; flagged for review due to ambiguity."
        )
    return (
        f"Classified as {category} based on {cited_cat} in the description"
        f"{urgency_note}."
    )


def _find_category_keyword(desc_lower: str, category: str) -> str | None:
    """Return the first keyword from description that maps to the given category."""
    keyword_map = {
        "Pothole":        ["pothole", "pot hole", "pit in road"],
        "Flooding":       ["flood", "waterlogging", "waterlogged", "submerged"],
        "Streetlight":    ["streetlight", "street light", "lamp post", "no light", "dark road"],
        "Waste":          ["garbage", "waste", "trash", "litter", "dumping", "rubbish"],
        "Noise":          ["noise", "loud", "sound", "disturbance", "honking"],
        "Road Damage":    ["road damage", "damaged road", "crack", "cracked road"],
        "Heritage Damage":["heritage", "monument", "historical", "ancient"],
        "Heat Hazard":    ["heat", "temperature", "hot pavement", "heat hazard"],
        "Drain Blockage": ["drain", "drainage", "sewer", "blocked drain"],
    }
    for kw in keyword_map.get(category, []):
        if kw in desc_lower:
            return kw
    return None


# ---------------------------------------------------------------------------
# Skill: batch_classify
# ---------------------------------------------------------------------------

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint to each row, write results CSV.

    Error handling (skills.md):
      - Logs row-level failures and continues; does not crash on bad rows.
      - Writes output even if some rows fail.
    """
    results = []
    error_count = 0

    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    error_count += 1
                    print(f"[ERROR] Row {i} failed: {e}", file=sys.stderr)
                    # Emit a NEEDS_REVIEW placeholder so the row isn't silently lost
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{i}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row processing error: {e}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"[FATAL] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    if error_count:
        print(f"[WARN] {error_count} row(s) had errors — check NEEDS_REVIEW flags.")


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

