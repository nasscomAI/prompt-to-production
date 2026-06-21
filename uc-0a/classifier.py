"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    # 1. Handle missing/null descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    # 2. Category Keywords Mapping
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlog", "rainwater"],
        "Streetlight": ["streetlight", "unlit", "lights out"],
        "Waste": ["garbage", "waste", "trash", "dead animal"],
        "Noise": ["music", "noise", "amplifier", "drilling", "sound", "idling"],
        "Road Damage": ["road surface", "footpath", "tarmac", "paving", "bridge approach", "cobblestone", "cracked and sinking"],
        "Heritage Damage": ["heritage", "historic", "ancient"],
        "Heat Hazard": ["heat", "temperature", "melting", "bubbling", "burns"],
        "Drain Blockage": ["drain", "manhole", "stormwater"]
    }

    matched_categories = []
    desc_lower = description.lower()
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                break  # Move to next category once a keyword matches

    # Determine final category and flag ambiguity
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 3. Priority Assignment
    # Urgent if severity keywords present
    severity_keywords = [
        "injury", "injured", "child", "children", "school", "hospital",
        "hospitalised", "ambulance", "fire", "hazard", "fell", "collapse", "collapsed"
    ]
    is_urgent = False
    for kw in severity_keywords:
        if kw in desc_lower:
            is_urgent = True
            break

    priority = "Urgent" if is_urgent else "Standard"

    # 4. Reason Extraction (One sentence citing specific words from description)
    # Split description into sentences using simple period-based splitting
    raw_sentences = description.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    reason = ""
    if sentences:
        # Try to find a sentence containing a keyword of the matched category
        keyword_found = False
        if len(matched_categories) == 1:
            keywords = category_keywords[category]
            for s in sentences:
                s_lower = s.lower()
                for kw in keywords:
                    if kw in s_lower:
                        reason = s
                        keyword_found = True
                        break
                if keyword_found:
                    break
        
        # Fallback to the first sentence if no keyword-matching sentence found
        if not reason:
            reason = sentences[0]
    else:
        reason = description

    # Ensure it ends with a period
    if reason and not reason.endswith('.'):
        reason += '.'

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
    """
    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}", file=sys.stderr)
                    # Create a fallback row so the process doesn't fail completely
                    results.append({
                        "complaint_id": row.get("complaint_id", "").strip(),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Classification failed due to internal error.",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    # Write output file
    try:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
