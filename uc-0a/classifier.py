"""
UC-0A Complaint Classifier
Classifies civic complaints by category, priority, reason, and flag
using strict taxonomy rules and severity keyword enforcement.
"""

import argparse
import csv
import re
import sys

# ── Strict taxonomy: only these exact strings are allowed ──
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# ── Severity keywords: presence → Urgent priority ──
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row):
    """Classify a single complaint row → category, priority, reason, flag."""
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()

    # ── 1. Determine Category (priority-ordered rule chain) ──
    category = "Other"
    evidence = []

    # Streetlight checks FIRST — catches "heritage street, lights out" correctly
    if any(kw in desc_lower for kw in ["streetlight", "lights out", "dark at night", "flickering", "sparking"]):
        category = "Streetlight"
        evidence = [w for w in ["streetlight", "lights out", "dark at night", "flickering", "sparking"] if w in desc_lower]
    elif "pothole" in desc_lower:
        category = "Pothole"
        evidence = ["pothole"]
    elif any(kw in desc_lower for kw in ["flood", "flooded", "waterlog", "standing in water", "knee-deep"]):
        category = "Flooding"
        evidence = [w for w in ["flood", "flooded", "waterlogging", "standing in water", "knee-deep"] if w in desc_lower]
    elif any(kw in desc_lower for kw in ["drain", "manhole"]):
        category = "Drain Blockage"
        evidence = [w for w in ["drain", "manhole"] if w in desc_lower]
    elif any(kw in desc_lower for kw in ["garbage", "waste", "dead animal", "overflowing", "bins"]):
        category = "Waste"
        evidence = [w for w in ["garbage", "waste", "dead animal", "overflowing", "bins"] if w in desc_lower]
    elif any(kw in desc_lower for kw in ["music", "noise", "loud"]):
        category = "Noise"
        evidence = [w for w in ["music", "noise", "loud"] if w in desc_lower]
    elif any(kw in desc_lower for kw in ["cracked", "sinking", "footpath", "tiles broken", "road surface"]):
        category = "Road Damage"
        evidence = [w for w in ["cracked", "sinking", "footpath", "tiles broken", "road surface"] if w in desc_lower]
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        evidence = ["heritage"]
    elif any(kw in desc_lower for kw in ["heat", "sunstroke"]):
        category = "Heat Hazard"
        evidence = [w for w in ["heat", "sunstroke"] if w in desc_lower]

    # Safety net: verify category is in allowed list
    if category not in ALLOWED_CATEGORIES:
        category = "Other"

    # ── 2. Determine Priority (ONLY severity keywords → Urgent) ──
    matched_severity = [
        kw for kw in SEVERITY_KEYWORDS
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)
    ]
    priority = "Urgent" if matched_severity else "Standard"

    # ── 3. Build Reason (must cite specific words from description) ──
    if matched_severity:
        reason = (
            f"Description contains severity keyword(s) '{', '.join(matched_severity)}' "
            f"→ Urgent. Category '{category}' based on '{', '.join(evidence)}'."
        )
    else:
        reason = (
            f"Category '{category}' assigned based on description keywords: "
            f"'{', '.join(evidence) if evidence else 'no strong match → Other'}'. "
            f"No severity keywords found → Standard priority."
        )

    # ── 4. Determine Flag ──
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    # Flag if description has overlapping category signals
    elif "heritage" in desc_lower and any(kw in desc_lower for kw in ["lights out", "streetlight", "dark"]):
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_file, output_file):
    """Read input CSV, classify each row, write enriched output CSV."""
    with open(input_file, mode="r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames)

        # Append classification output columns
        for col in ["category", "priority", "reason", "flag"]:
            if col not in fieldnames:
                fieldnames.append(col)

        rows = []
        urgent_count = 0
        review_count = 0

        for row in reader:
            res = classify_complaint(row)
            row["category"] = res["category"]
            row["priority"] = res["priority"]
            row["reason"] = res["reason"]
            row["flag"] = res["flag"]
            rows.append(row)

            if res["priority"] == "Urgent":
                urgent_count += 1
            if res["flag"] == "NEEDS_REVIEW":
                review_count += 1

    with open(output_file, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    standard_count = len(rows) - urgent_count
    print(f"Classified {len(rows)} complaints. Urgent: {urgent_count}, Standard: {standard_count}, NEEDS_REVIEW: {review_count}")
    print(f"Output written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
