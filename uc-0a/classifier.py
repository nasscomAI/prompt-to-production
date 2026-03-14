"""
UC-0A — Complaint Classifier
Built from agents.md (RICE) and skills.md skill contracts.
"""
import argparse
import csv

# ── Schema constants (agents.md enforcement rules 1 & 2) ─────────────────────

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
}

OUTPUT_FIELDS = ["category", "priority", "reason", "flag"]


# ── Skill: classify_complaint ─────────────────────────────────────────────────
# Contract (skills.md):
#   Input : one complaint row dict with a 'description' key (plain text).
#   Output: dict with keys — category, priority, reason, flag.
#   Error handling: empty/missing description → Other / Low / NEEDS_REVIEW.

def classify_complaint(row: dict) -> dict:
    description: str = (row.get("description") or "").strip()

    # ── Error handling: empty or missing description ──────────────────────────
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Description field was empty or missing; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Enforcement rule 2: severity keyword → Urgent ─────────────────────────
    matched_keywords = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if matched_keywords else "Standard"

    # ── Enforcement rule 1: category — exact taxonomy strings only ────────────
    category_rules = [
        ("Pothole",         ["pothole", "pot hole", "crater", "pit in road"]),
        ("Flooding",        ["flood", "waterlog", "inundated", "submerged", "water logging"]),
        ("Streetlight",     ["streetlight", "street light", "lamp post", "light out", "no light", "dark road"]),
        ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter", "dump", "overflowing bin"]),
        ("Noise",           ["noise", "loud", "sound", "honking", "music", "disturbance"]),
        ("Road Damage",     ["road damage", "damaged road", "broken road", "cracked road", "road crack"]),
        ("Heritage Damage", ["heritage", "monument", "historical", "ancient", "temple wall", "old building"]),
        ("Heat Hazard",     ["heat", "hot", "temperature", "summer", "heat wave", "scorching"]),
        ("Drain Blockage",  ["drain", "sewer", "blocked drain", "clogged", "overflow", "manhole"]),
    ]

    category = None
    evidence = None
    for cat, keywords in category_rules:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                evidence = kw
                break
        if category:
            break

    # ── Enforcement rule 4: ambiguous → Other + NEEDS_REVIEW ─────────────────
    flag = ""
    if category is None:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = (
            f"No recognisable category keyword found in: "
            f"\"{description[:80]}\"; marked for manual review."
        )
    else:
        # ── Enforcement rule 3: reason must cite words from the description ────
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
#   Output: CSV at output_path — all original columns + category, priority,
#           reason, flag appended for every row.
#   Error handling: malformed rows get Other / Low / NEEDS_REVIEW;
#                   processing continues without halting.

def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        original_fields = reader.fieldnames or []

        for i, row in enumerate(reader, start=1):
            try:
                classification = classify_complaint(row)
            except Exception as exc:
                classification = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row {i} raised an unexpected error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }

            out_row = {field: row.get(field, "") for field in original_fields}
            out_row.update(classification)
            results.append(out_row)

    all_fields = list(original_fields) + [
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
