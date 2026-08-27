"""
UC-0A — Complaint Classifier
Built from agents.md (RICE) and skills.md skill contracts.

Agent role   : Civic complaint classifier — read one description, produce a
               four-field classification record.  No action, no escalation.
Agent intent : category · priority · reason · flag — every field present,
               every value schema-exact, reason traceable to input text.
Agent context: Only the description field is used — never city, ward, row
               number, or complainant identity.
"""
import argparse
import csv

# ── Schema constants (agents.md enforcement rules 1 & 2) ─────────────────────

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Enforcement rule 2: these keywords MUST trigger Urgent priority.
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
}

OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]


# ── Skill: classify_complaint ─────────────────────────────────────────────────
# Contract (skills.md):
#   Input : one complaint row dict with a 'description' key (plain text).
#   Output: dict with keys — category, priority, reason, flag.
#   Error handling:
#     - Empty or missing description → category: Other, priority: Low,
#       flag: NEEDS_REVIEW, reason states description was insufficient.
#     - Never raise an unhandled error.

def classify_complaint(row: dict) -> dict:
    description: str = str((row.get("description") or "")).strip()

    # ── Error handling: empty or missing description ──────────────────────────
    # skills.md: "If the description is empty or missing, return category:
    # Other, priority: Low, flag: NEEDS_REVIEW, and a reason stating the
    # description was insufficient — never raise an unhandled error."
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description field was empty or missing; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower: str = str(description).lower()

    # ── Enforcement rule 2: severity keyword → Urgent ─────────────────────────
    # agents.md enforcement: "Priority must be set to Urgent if and only if
    # the description contains at least one of these keywords: injury, child,
    # school, hospital, ambulance, fire, hazard, fell, collapse."
    matched_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if matched_keywords else "Standard"

    # ── Enforcement rule 1: category — exact taxonomy strings only ────────────
    # agents.md enforcement: "Category must be exactly one of: Pothole ·
    # Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage ·
    # Heat Hazard · Drain Blockage · Other — no variations, abbreviations, or
    # synonyms."
    #
    # Each tuple: (exact_category_string, [trigger_phrases_in_lowercase])
    # Phrases are checked in order; first match wins.
    category_rules = [
        ("Pothole",         ["pothole", "pot hole", "crater", "pit in road"]),
        ("Flooding",        ["flood", "waterlog", "inundated", "submerged", "water logging"]),
        ("Streetlight",     ["streetlight", "street light", "lamp post", "light out", "no light", "dark road"]),
        ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter", "dump", "overflowing bin",
                             "dead animal", "overflowing garbage"]),
        ("Noise",           ["noise", "loud", "sound", "honking", "music", "disturbance"]),
        ("Road Damage",     ["road damage", "damaged road", "broken road", "cracked road", "road crack",
                             "road surface cracked", "sinking"]),
        ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "temple wall", "old building"]),
        ("Heat Hazard",     ["heat", "hot", "temperature", "summer", "heat wave", "scorching"]),
        ("Drain Blockage",  ["drain", "sewer", "blocked drain", "clogged", "overflow", "manhole"]),
    ]

    category = None
    evidence = None
    for cat, keywords in category_rules:
        for phrase in keywords:
            if phrase in desc_lower:
                category = cat
                evidence = phrase
                break
        if category:
            break

    # ── Enforcement rule 4: ambiguous → Other + NEEDS_REVIEW ─────────────────
    # agents.md enforcement: "If the correct category cannot be determined
    # from the description alone, output category: Other and
    # flag: NEEDS_REVIEW — never guess with false confidence."
    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
        # ── Enforcement rule 3 (NEEDS_REVIEW path): reason must still cite ────
        # words from the description and, if applicable, the severity keywords
        # that determined priority.
        snippet: str = description[0:80]
        if matched_keywords:
            reason = (
                f'No recognisable category keyword found in: "{snippet}"; '
                f"priority set to Urgent due to severity keyword(s): "
                f"{', '.join(matched_keywords)}; marked for manual review."
            )
        else:
            reason = (
                f'No recognisable category keyword found in: "{snippet}"; '
                f"marked for manual review."
            )
    else:
        # ── Enforcement rule 3 (classified path): reason must cite specific ───
        # words or phrases directly from the complaint description.
        if matched_keywords:
            reason = (
                f"Classified as {category} because the description mentions "
                f"\"{evidence}\"; priority set to Urgent due to "
                f"severity keyword(s): {', '.join(matched_keywords)}."
            )
        else:
            reason = (
                f"Classified as {category} because the description contains "
                f"the term \"{evidence}\"."
            )

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Skill: batch_classify ─────────────────────────────────────────────────────
# Contract (skills.md):
#   Input : file path to a CSV with at least a 'description' column.
#           (15 rows per city; category and priority_flag columns are stripped
#           in test files.)
#   Output: CSV at output_path — all original columns + category, priority,
#           reason, flag appended for every row.
#   Error handling:
#     - Malformed row or missing description field → category: Other,
#       priority: Low, flag: NEEDS_REVIEW, descriptive reason.
#     - Processing continues without halting on any single-row error.

def batch_classify(input_path: str, output_path: str) -> None:
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fields = list(reader.fieldnames or [])

        for i, row in enumerate(reader, start=1):
            try:
                classification = classify_complaint(row)
            except Exception as exc:
                # skills.md: "write category: Other, priority: Low,
                # flag: NEEDS_REVIEW, and a descriptive reason — then continue
                # processing all remaining rows without halting."
                classification = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row {i} raised an unexpected error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            out_row = {field: row.get(field, "") for field in original_fields}
            out_row.update(classification)
            results.append(out_row)

    # Preserve all original columns; append output fields not already present.
    all_fields = original_fields + [
        f for f in OUTPUT_FIELDS if f not in original_fields
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(results)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
