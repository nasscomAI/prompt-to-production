"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re


SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste",
    "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]


CATEGORY_KEYWORDS = [
    # More specific categories first to avoid false matches
    ("Drain Blockage", ["drain blockage", "drain blocked", "clogged drain", "blocked drain"]),
    ("Road Damage", ["road damage", "cave-in", "sunken road", "road collapsed"]),
    ("Heritage Damage", ["heritage", "historical", "monument", "old building"]),
    ("Heat Hazard", ["heat hazard", "heatwave", "scorching", "extreme heat"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "streetlamp"]),
    ("Noise", ["noise", "loud", "shouting", "disturbance"]),
    ("Waste", ["waste", "garbage", "trash", "dump", "bin overflow"]),
    ("Pothole", ["pothole", "road crack", "asphalt damage"]),
    ("Flooding", ["flood", "waterlogged", "knee-deep", "stranded"]),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md / README):
    - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    - Priority must be Urgent if description contains severity keywords
    - Reason must be one sentence citing specific words from description
    - Flag must be NEEDS_REVIEW when category is genuinely ambiguous, blank otherwise
    """
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "")

    category = _classify_category(description)
    priority = _classify_priority(description)
    reason = _generate_reason(description, category)
    flag = _determine_flag(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _classify_category(description: str) -> str:
    """Classify the complaint category based on keywords in the description."""
    desc = description.lower()

    # Check more specific categories first to avoid false matches
    for cat, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in desc:
                return cat

    # Default to Other if nothing specific matches
    return "Other"


def _classify_priority(description: str) -> str:
    """Priority: Urgent if severity keywords present, otherwise Standard."""
    desc = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            return "Urgent"
    return "Standard"


def _generate_reason(description: str, category: str) -> str:
    """Generate one sentence reason citing specific words from the description."""
    desc = description.lower()

    # Find matching category keywords in description
    for cat, keywords in CATEGORY_KEYWORDS:
        if cat == category:
            found_words = [w for w in keywords if w in desc]
            if found_words:
                reason = "Issue identified: " + " and ".join(found_words) + " mentioned in complaint"
            else:
                # Fallback: cite first few words from description
                words = desc.split()[:8]
                reason = "Issue identified: " + " ".join(words)
            break
    else:
        words = desc.split()[:8]
        reason = "Issue identified: " + " ".join(words)

    # Ensure it's one sentence
    reason = reason.strip().rstrip(".!?") + "."
    return reason


def _determine_flag(description: str, category: str) -> str:
    """Determine flag: NEEDS_REVIEW when genuinely ambiguous, blank otherwise."""
    desc = description.lower()

    # Genuinely ambiguous descriptions that need review
    ambiguous_keywords = ["mixed", "multiple", "several", "various", "combination"]
    if any(kw in desc for kw in ambiguous_keywords):
        return "NEEDS_REVIEW"

    # If category is Other, it may need review
    if category == "Other":
        return "NEEDS_REVIEW"

    return ""


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Determine output directory and ensure it exists
    import os
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Classify each row, handling errors gracefully
    results = []
    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            print(f"Warning: Row {i} could not be classified: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", f"row-{i}"),
                "category": "Other",
                "priority": "Standard",
                "reason": "Failed to classify — " + str(e),
                "flag": "NEEDS_REVIEW",
            })

    # Write results CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return

    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
