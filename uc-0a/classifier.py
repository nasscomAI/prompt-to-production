"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and review flag.
"""
import argparse
import csv
import re
import sys

VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Drain Blockage": ["drain blocked", "drain blockage", "drain 100% blocked", "drain completely blocked", "drain blocked and", "manhole", "sewer"],
    "Pothole": ["pothole", "potholes", "tyre damage", "road surface broken"],
    "Flooding": ["flood", "flooded", "flooding", "knee-deep", "waterlogged", "water logging", "stranded", r"\brain\b", r"\brainwater\b"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "dark at night", "sparking"],
    "Waste": ["garbage", "waste", "overflowing bins", "dead animal", "dumped", "renovation dumped", "not cleared"],
    "Noise": ["noise", "music", "loud", "midnight", "weeknights", "disturbance", "drilling", "idling", "engines on", "horn"],
    "Road Damage": ["road surface cracked", "sinking", "road damaged", "footpath tiles broken", "upturned", "collapsed", "crater", "road collapse"],
    "Heritage Damage": ["heritage building damaged", "heritage structure", "heritage monument", "vandalized heritage", "graffiti on heritage", "heritage street damaged"],
    "Heat Hazard": ["heat", "heatwave", "scorching", "sunstroke"],
}

REVIEW_KEYWORDS = [
    "could be", "might be", "possibly", "unclear", "ambiguous",
    "not sure", "uncertain", "hard to tell"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description missing",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Determine category — use the earliest matching keyword across all categories
    category = "Other"
    matched_evidence = ""
    best_pos = None
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            m = re.search(kw, desc_lower)
            if m and (best_pos is None or m.start() < best_pos):
                best_pos = m.start()
                category = cat
                matched_evidence = m.group(0)

    # Ambiguity check
    is_ambiguous = any(kw in desc_lower for kw in REVIEW_KEYWORDS)
    # Also flag if no strong keyword match was found for non-Other categories
    if category == "Other" and not is_ambiguous:
        is_ambiguous = True

    # Determine priority
    priority = "Standard"
    severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if severity_found:
        priority = "Urgent"

    # Build reason — cite specific words from description
    if matched_evidence:
        reason = f"Description mentions '{matched_evidence}' which indicates {category.lower()}"
    elif severity_found:
        reason = f"Description mentions '{severity_found[0]}' indicating urgency"
    else:
        # Extract a key phrase from the description
        words = description.split()
        phrase = " ".join(words[:8]) if len(words) > 8 else description
        reason = f"Description discusses: {phrase}"

    # Determine flag
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for i, row in enumerate(rows, start=1):
        try:
            if not row.get("complaint_id"):
                print(f"Row {i}: Missing complaint_id, skipping", file=sys.stderr)
                continue
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            print(f"Row {i}: Error classifying — {e}", file=sys.stderr)
            continue

    if not results:
        print("Warning: No valid rows classified", file=sys.stderr)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)}/{len(rows)} complaints -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
