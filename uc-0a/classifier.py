"""
UC-0A — Complaint Classifier
Generated from agents.md (role / intent / context / enforcement) and
skills.md (classify_complaint / batch_classify).

Agent contract (agents.md):
  - Uses ONLY the description field — no other columns.
  - Category must be exactly one of the 10 allowed values.
  - Priority is Urgent if any severity keyword appears (case-insensitive).
  - Every row must include a reason quoting words from the description.
  - Ambiguous descriptions get category=Other and flag=NEEDS_REVIEW.
"""
import argparse
import csv
import re

# ── Enforcement: allowed categories (agents.md rule 1) ───────────────────────
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

# ── Enforcement: severity keywords → Urgent (agents.md rule 2) ───────────────
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Category keyword map (ordered: most-specific first) ──────────────────────
# Each entry: (category, [trigger keywords])
CATEGORY_RULES = [
    ("Drain Blockage",  ["drain blocked", "drain blockage", "blocked drain",
                         "drain completely blocked", "drainage blocked", "clogged drain"]),
    ("Flooding",        ["flood", "flooded", "flooding", "waterlogged",
                         "inundated", "water logging", "submerged"]),
    ("Pothole",         ["pothole", "pot hole", "potholes", "crater in road"]),
    ("Heritage Damage", ["heritage", "historic", "historical", "monument",
                         "heritage lamp", "tram road", "cobblestone"]),
    ("Heat Hazard",     ["heat", "temperature", "melting", "hot surface",
                         "burning surface", "tarmac melting", "overheating"]),
    ("Streetlight",     ["streetlight", "street light", "lamp post", "lamp",
                         "lighting", "light not working", "lights out"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "litter",
                         "dumping", "dump", "refuse"]),
    ("Noise",           ["noise", "loud", "sound", "nuisance", "disturbance",
                         "blaring", "honking"]),
    ("Road Damage",     ["road damage", "road surface", "tarmac", "asphalt",
                         "pavement broken", "broken road", "road broken",
                         "surface damage", "road crack"]),
]


def _find_trigger(description: str, keywords: list) -> str:
    """Return the first matching keyword found in description, or empty string."""
    desc_lower = description.lower()
    for kw in keywords:
        if kw.lower() in desc_lower:
            return kw
    return ""


def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint (skills.md)

    Input : dict with at least 'complaint_id' and 'description' keys.
    Output: dict with keys — category, priority, reason, flag.

    Error handling (skills.md):
      - Missing / empty description → Other, Low, NEEDS_REVIEW.
      - Never raises — always returns a valid dict.
    """
    description = (row.get("description") or "").strip()

    # ── Error handling: empty description ────────────────────────────────────
    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason":   "No description provided.",
            "flag":     "NEEDS_REVIEW",
        }

    # ── Enforcement rule 2: check for severity keywords → Urgent ─────────────
    urgent_trigger = _find_trigger(description, URGENT_KEYWORDS)
    priority = "Urgent" if urgent_trigger else "Standard"

    # ── Enforcement rule 1: match category via keyword rules ─────────────────
    matched_category = None
    matched_trigger  = None
    match_count      = 0

    for category, keywords in CATEGORY_RULES:
        trigger = _find_trigger(description, keywords)
        if trigger:
            match_count += 1
            if matched_category is None:
                matched_category = category
                matched_trigger  = trigger

    # ── Enforcement rule 4: ambiguous → Other + NEEDS_REVIEW ─────────────────
    if match_count > 1 or matched_category is None:
        flag     = "NEEDS_REVIEW"
        category = "Other"
        reason_parts = [f'Description states: "{description[:120]}"']
        if match_count > 1:
            reason_parts.append("Multiple categories matched — cannot determine single category.")
        else:
            reason_parts.append("No category keyword matched.")
        reason = " ".join(reason_parts)
    else:
        flag     = ""
        category = matched_category
        # ── Enforcement rule 3: reason must quote words from description ──────
        reason = (
            f'Classified as {category} because description contains '
            f'"{matched_trigger}"'
        )
        if urgent_trigger:
            reason += f'; marked Urgent due to "{urgent_trigger}"'
        reason += "."

    return {
        "category": category,
        "priority": priority,
        "reason":   reason,
        "flag":     flag,
    }


def batch_classify(input_path: str, output_path: str) -> int:
    """
    Skill: batch_classify (skills.md)

    Input : input_path — CSV with complaint_id + description columns.
            output_path — path to write results CSV.
    Output: results CSV with columns complaint_id, category, priority, reason, flag.
            Returns count of rows successfully classified.

    Error handling (skills.md):
      - Row-level failure → fallback row written, processing continues.
      - Unreadable input file → raises FileNotFoundError.
      - Never silently skips rows.
    """
    import os
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    success_count = 0

    with open(input_path,  newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            complaint_id = row.get("complaint_id", f"ROW-{i}")
            try:
                result = classify_complaint(row)
                writer.writerow({
                    "complaint_id": complaint_id,
                    "category":     result["category"],
                    "priority":     result["priority"],
                    "reason":       result["reason"],
                    "flag":         result["flag"],
                })
                success_count += 1
            except Exception as exc:
                # skills.md: write fallback row, never skip
                writer.writerow({
                    "complaint_id": complaint_id,
                    "category":     "Other",
                    "priority":     "Low",
                    "reason":       "Classification error.",
                    "flag":         "NEEDS_REVIEW",
                })
                print(f"  Warning: row {i} ({complaint_id}) failed — {exc}")

    return success_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    count = batch_classify(args.input, args.output)
    print(f"Done. {count} rows classified. Results written to {args.output}")
