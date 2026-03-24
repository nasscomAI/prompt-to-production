"""
UC-0A — Complaint Classifier (Rule-Based, no API key required)
Implements the RICE enforcement rules from agents.md via keyword matching.
"""
import argparse
import csv
import re

# ── Enforcement rules from agents.md ─────────────────────────────────────────

# Priority: Urgent if ANY of these words appear in the description
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword map — evaluated in order; first match wins
CATEGORY_RULES = [
    ("Pothole",          ["pothole", "crater", "pit", "deep hole", "sunken"]),
    ("Flooding",         ["flood", "waterlog", "waterlogged", "submerge", "overflow", "inundated"]),
    ("Streetlight",      ["streetlight", "street light", "lamp", "light not working", "dark road", "bulb"]),
    ("Waste",            ["garbage", "waste", "trash", "dump", "litter", "rubbish", "smell", "stench", "decaying"]),
    ("Noise",            ["noise", "loud", "horn", "music blaring", "sound", "blasting", "disturbance"]),
    ("Road Damage",      ["road damage", "road crack", "broken road", "damaged road", "tar", "asphalt", "uneven road", "road caved"]),
    ("Heritage Damage",  ["heritage", "monument", "historical", "ancient", "protected structure"]),
    ("Heat Hazard",      ["heat", "burning", "hot surface", "temperature", "overheating"]),
    ("Drain Blockage",   ["drain", "blocked drain", "clog", "sewer", "manhole", "drainage"]),
]

VALID_CATEGORIES = {r[0] for r in CATEGORY_RULES} | {"Other"}

# ── Skill: classify_complaint ─────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Enforcement rules from agents.md applied via keyword matching.
    """
    description = str(row.get("description", "")).strip()
    complaint_id = row.get("complaint_id", "")
    desc_lower = description.lower()

    # Determine category — first matching rule wins
    category = "Other"
    matched_keyword = None
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_keyword = kw
                break
        if matched_keyword:
            break

    # Determine priority — Urgent if any severity keyword is present
    triggered_severity = next(
        (kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)),
        None
    )
    priority = "Urgent" if triggered_severity else "Standard"

    # Build reason — cites specific words from description (agents.md rule)
    if category != "Other" and matched_keyword:
        reason = (
            f"Classified as '{category}' because the description contains "
            f"the keyword '{matched_keyword}'."
        )
        if triggered_severity:
            reason = reason.rstrip('.') + f", and marked Urgent due to severity keyword '{triggered_severity}'."
        flag = ""
    else:
        # Genuinely ambiguous — cannot determine from description alone
        reason = "No matching category keywords found in the description; flagged for human review."
        priority = "Low"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

# ── Skill: batch_classify ─────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint per row, write results CSV.
    Skips malformed/empty rows with a NEEDS_REVIEW flag; never crashes.
    """
    results = []

    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for i, row in enumerate(reader):
                c_id = row.get("complaint_id", str(i))
                row["complaint_id"] = c_id

                # Handle null or empty descriptions
                if not row.get("description") or str(row.get("description")).strip() == "":
                    print(f"  [SKIP] Row {c_id} has no description.")
                    results.append({
                        "complaint_id": c_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing or null description; cannot classify.",
                        "flag": "NEEDS_REVIEW",
                    })
                    continue

                print(f"  Classifying {c_id}...")
                results.append(classify_complaint(row))

    except Exception as e:
        print(f"Error reading input file '{input_path}': {e}")
        return

    # Write output CSV
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file '{output_path}': {e}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (rule-based)")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
