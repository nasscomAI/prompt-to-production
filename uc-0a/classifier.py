"""
UC-0A — Complaint Classifier
Implements RICE framework from agents.md with skills from skills.md.
"""
import argparse
import csv
import sys

# Allowed categories (exact match required)
ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

# Keywords for urgent priority
URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Implements RICE enforcement rules from agents.md:
    - Category must be exactly one of the allowed 10 categories
    - Priority is Urgent if urgent keywords present, otherwise Standard/Low
    - Reason must cite specific words from description
    - Flag NEEDS_REVIEW only for genuinely ambiguous cases
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower()

    # Handle missing description
    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Determine category based on keywords in description
    category = "Other"
    reason = ""
    flag = ""

    # Category classification logic
    if "pothole" in description:
        category = "Pothole"
        reason = "Description mentions 'pothole'"
    elif "flood" in description or "flooded" in description or "knee-deep" in description:
        category = "Flooding"
        reason = "Description mentions flooding or water accumulation"
    elif "streetlight" in description or ("light" in description and ("out" in description or "dark" in description or "flickering" in description or "sparking" in description)):
        category = "Streetlight"
        reason = "Description mentions streetlight issues or lighting problems"
    elif "garbage" in description or "waste" in description or "overflowing" in description and "bin" in description:
        category = "Waste"
        reason = "Description mentions garbage or waste management issues"
    elif "music" in description or "noise" in description or "midnight" in description:
        category = "Noise"
        reason = "Description mentions noise or sound disturbance"
    elif "road" in description and ("crack" in description or "sinking" in description or "surface" in description or "damage" in description):
        category = "Road Damage"
        reason = "Description mentions road surface damage"
    elif "heritage" in description:
        category = "Heritage Damage"
        reason = "Description mentions heritage concerns"
    elif "heat" in description:
        category = "Heat Hazard"
        reason = "Description mentions heat-related issues"
    elif "drain" in description or "manhole" in description:
        category = "Drain Blockage"
        reason = "Description mentions drain or manhole issues"
    elif "footpath" in description or "tiles" in description or "broken" in description:
        category = "Road Damage"
        reason = "Description mentions broken footpath or tiles"
    elif "animal" in description or "health" in description:
        category = "Waste"
        reason = "Description mentions dead animal or health concern"
    elif "bulk waste" in description or "dumped" in description:
        category = "Waste"
        reason = "Description mentions bulk waste or illegal dumping"
    elif "bridge" in description and "flood" in description:
        category = "Flooding"
        reason = "Description mentions bridge flooding"
    else:
        category = "Other"
        reason = "Cannot confidently classify from description"
        flag = "NEEDS_REVIEW"

    # Determine priority based on urgent keywords
    priority = "Standard"
    urgent_found = []

    for keyword in URGENT_KEYWORDS:
        if keyword in description:
            urgent_found.append(keyword)

    if urgent_found:
        priority = "Urgent"
        if reason and not flag:
            reason = f"{reason}, contains urgent keyword(s): {', '.join(urgent_found)}"
    else:
        # Assign Standard or Low based on severity indicators
        if "risk" in description or "stranded" in description or "safety" in description:
            priority = "Standard"
        else:
            priority = "Low"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Error handling:
    - Skips rows with missing complaint_id
    - Continues processing even if individual rows fail
    - Always produces output file
    """
    results = []

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    if not row.get("complaint_id"):
                        print(f"Warning: Skipping row with missing complaint_id", file=sys.stderr)
                        continue

                    result = classify_complaint(row)
                    results.append(result)

                except Exception as e:
                    print(f"Warning: Failed to classify complaint {row.get('complaint_id', 'UNKNOWN')}: {e}", file=sys.stderr)
                    # Add a fallback result
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        raise

    # Write results
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
