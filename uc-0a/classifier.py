"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
Classifies citizen complaints by category, priority, reason, and flag.
"""
import argparse
import csv
import sys

# Allowed categories — exact strings only, as defined in agents.md
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

# Severity keywords that MUST trigger Urgent priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword → category mapping for deterministic classification
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogging", "waterlogged", "knee-deep", "inundated", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp", "light out", "lights out", "lighting", "sparking", "flickering"],
    "Waste": ["garbage", "waste", "rubbish", "trash", "dump", "litter", "bins", "overflowing", "animal", "dead animal"],
    "Noise": ["noise", "music", "sound", "loud", "midnight", "night", "playing"],
    "Road Damage": ["road", "cracked", "sinking", "surface", "manhole", "footpath", "tiles", "broken", "upturned", "pavement", "tarmac"],
    "Heritage Damage": ["heritage", "old city", "historic", "ancient", "monument"],
    "Heat Hazard": ["heat", "temperature", "sun", "hot", "scorching"],
    "Drain Blockage": ["drain", "drainage", "sewer", "blocked", "blockage", "clog"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    RICE enforcement rules from agents.md:
    1. Category must be exactly one of the allowed values
    2. Priority must be Urgent if any severity keyword is present
    3. Every output must include reason citing specific words from description
    4. Flag NEEDS_REVIEW if genuinely ambiguous
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description field is empty — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- STEP 1: Determine priority (must check BEFORE category) ---
    priority = "Standard"
    urgent_word_found = None
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            urgent_word_found = kw
            break

    # --- STEP 2: Determine category ---
    matched_categories = []
    matched_words = {}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_words[cat] = kw
                break

    # Special override: streetlight flickering/sparking on heritage street → Streetlight
    # (heritage + lights → Heritage Damage takes precedence if "heritage" explicitly in text)
    if "Heritage Damage" in matched_categories and "Streetlight" in matched_categories:
        if "heritage" in desc_lower:
            matched_categories = ["Heritage Damage"]
        else:
            matched_categories = ["Streetlight"]

    # --- STEP 3: Resolve category ---
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
        trigger_word = matched_words[category]
        reason = f'Classified as {category} because the description mentions "{trigger_word}"'
        if urgent_word_found:
            reason += f' and contains urgency keyword "{urgent_word_found}".'
        else:
            reason += "."
    elif len(matched_categories) > 1:
        # Multiple matches — pick highest priority match or flag as ambiguous
        # Priority order matches CATEGORY_KEYWORDS order
        category = matched_categories[0]
        trigger_word = matched_words[category]
        flag = "NEEDS_REVIEW"
        cats_str = ", ".join(matched_categories)
        reason = (
            f'Complaint matches multiple categories ({cats_str}); '
            f'primary classification as {category} based on "{trigger_word}" '
            f'but flagged for human review.'
        )
    else:
        # No keyword match
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f'No matching category keyword found in description — classified as Other for human review.'

    # Override priority to Urgent if urgent keyword found (enforce regardless of category)
    if urgent_word_found and priority != "Urgent":
        priority = "Urgent"

    # If priority was Standard but no urgent keywords and complaint is minor → Low
    if priority == "Standard":
        # Noise complaints and minor issues that don't include any urgency → Low priority
        if category == "Noise" and urgent_word_found is None:
            priority = "Low"

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
    Does not crash on bad rows — produces output even if some rows fail.
    """
    results = []
    failed_count = 0
    total_count = 0

    try:
        with open(input_path, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    for row in rows:
        total_count += 1
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            failed_count += 1
            results.append({
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "Other",
                "priority": "Low",
                "reason": f"Processing error: {str(e)}",
                "flag": "NEEDS_REVIEW",
            })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Processed {total_count} complaints. Failed rows: {failed_count}.")
    if failed_count > 0:
        print(f"WARNING: {failed_count} row(s) could not be classified — marked NEEDS_REVIEW.")

    # Print summary of classifications
    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Urgent: {urgent_count} | NEEDS_REVIEW: {review_count} | Total: {total_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
