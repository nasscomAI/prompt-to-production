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


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforcement rules (from agents.md / README):
    - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    - Priority must be Urgent if description contains severity keywords
    - Reason must be one sentence citing specific words from description
    - Flag must be NEEDS_REVIEW when category is genuinely ambiguous, blank otherwise
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "")

    # Step 1: Determine category — find the best matching category from description
    category = _classify_category(description)

    # Step 2: Determine priority — Urgent if severity keywords present
    priority = _classify_priority(description)

    # Step 3: Generate reason — one sentence citing specific words from description
    reason = _generate_reason(description, category)

    # Step 4: Determine flag — NEEDS_REVIEW when genuinely ambiguous
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

    # Check for each category with keyword mapping
    category_keywords = {
        "Pothole": ["pothole", "road", "crack", "asphalt"],
        "Flooding": ["flood", "water", "rain", "drain", "knee-deep", "stranded"],
        "Streetlight": ["streetlight", "light", "dark", "out", "lighting"],
        "Waste": ["waste", "garbage", "trash", "dump", "bin"],
        "Noise": ["noise", "loud", "shouting", "disturb"],
        "Road Damage": ["road damage", "cave-in", "sunken road"],
        "Heritage Damage": ["heritage", "historical", "monument", "old building"],
        "Heat Hazard": ["heat", "hot", "scorching", "sun"],
        "Drain Blockage": ["drain", "blocked", "clogged", "water logging"],
    }

    # Also check for "Other" — if no specific category matches, use Other
    # But first check for explicit category mentions
    for cat, keywords in category_keywords.items():
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
    desc = description

    # Extract key phrases based on category
    category_keywords = {
        "Pothole": ["pothole", "60cm", "wide", "tyre damage"],
        "Flooding": ["flooded", "knee-deep", "stranded", "rain"],
        "Streetlight": ["streetlights", "out", "dark", "10 days"],
        "Waste": ["waste", "garbage", "trash"],
        "Noise": ["noise", "loud"],
        "Road Damage": ["road damage", "cave-in"],
        "Heritage Damage": ["heritage", "historical"],
        "Heat Hazard": ["heat", "hot"],
        "Drain Blockage": ["drain", "blocked", "clogged"],
    }

    keywords = category_keywords.get(category, [])
    found_words = [w for w in keywords if w.lower() in desc.lower()]

    if found_words:
        # Build a simple reason citing the found words
        reason_parts = []
        if "pothole" in found_words or "60cm" in found_words:
            reason_parts.append("pothole issue")
        if "flooded" in found_words or "knee-deep" in found_words:
            reason_parts.append("flooded area")
        if "streetlight" in found_words or "out" in found_words:
            reason_parts.append("streetlight out")
        if "waste" in found_words or "garbage" in found_words:
            reason_parts.append("waste issue")
        if "noise" in found_words or "loud" in found_words:
            reason_parts.append("noise complaint")
        if "road damage" in found_words or "cave-in" in found_words:
            reason_parts.append("road damage")
        if "heritage" in found_words or "historical" in found_words:
            reason_parts.append("heritage issue")
        if "heat" in found_words or "hot" in found_words:
            reason_parts.append("heat hazard")
        if "drain" in found_words or "blocked" in found_words:
            reason_parts.append("drain blockage")

        if reason_parts:
            reason = "Observed " + " and ".join(reason_parts) + " in description"
        else:
            reason = "Issue identified from complaint description"
    else:
        # Fallback: cite a few words from the description
        words = desc.split()[:5]
        reason = "Issue identified: " + " ".join(words)

    # Ensure it's one sentence
    reason = reason.strip().rstrip(".!?") + "."

    return reason


def _determine_flag(description: str, category: str) -> str:
    """Determine flag: NEEDS_REVIEW when genuinely ambiguous, blank otherwise."""
    desc = description.lower()

    # Genuinely ambiguous categories that need review
    ambiguous_keywords = ["mixed", "multiple", "several", "various", "combination"]
    if any(kw in desc for kw in ambiguous_keywords):
        return "NEEDS_REVIEW"

    # If category is Other, it may need review
    if category == "Other":
        # Check if description contains clear category indicators
        clear_categories = ["pothole", "flood", "streetlight", "waste", "noise"]
        if not any(c in desc for c in clear_categories):
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
    output_dir = "/".join(output_path.split("/")[:-1])
    try:
        import os
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    except Exception:
        pass

    # Classify each row, handling errors gracefully
    results = []
    for i, row in enumerate(rows):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            # If a row fails, create a minimal result with flag indicating issue
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

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
