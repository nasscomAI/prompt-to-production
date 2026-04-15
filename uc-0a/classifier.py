"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
from typing import Dict

def classify_complaint(row: Dict[str, str]) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # Follow agents.md enforcement and skills.md specifications
    description = (row.get("description") or "").strip()
    desc_lower = description.lower()

    # Exact allowed categories (reverted per latest agents.md)
    categories = {
        'pothole': 'Pothole',
        'potholes': 'Pothole',
        'pothole(s)': 'Pothole',
        'flood': 'Flooding',
        'flooding': 'Flooding',
        'streetlight': 'Streetlight',
        'street lights': 'Streetlight',
        'light': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'trash': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'road damage': 'Road Damage',
        'road': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'temperature': 'Heat Hazard',
        'temprature': 'Heat Hazard',
        'drain': 'Drain Blockage',
        'drainage': 'Drain Blockage',
        'sewer': 'Drain Blockage',
        'blocked drain': 'Drain Blockage',
    }

    # Priority keywords (updated per latest agents.md)
    urgent_kw = ['hospital', 'ambulance', 'fire', 'heat hazard', 'fell', 'collapse']
    standard_kw = ['injury', 'road', 'child', 'school', 'pothole', 'dark', 'flood']
    low_kw = ['paving', 'heritage', 'waste', 'crater', 'music']

    matched_cats = set()
    matched_words = []
    for kw, cat in categories.items():
        if kw in desc_lower:
            matched_cats.add(cat)
            matched_words.append(kw)

    # Determine category and flag for ambiguity
    if not description:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    elif len(matched_cats) == 1:
        category = next(iter(matched_cats))
        flag = ''
    elif len(matched_cats) > 1:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'

    # Determine priority
    low_found = any(k in desc_lower for k in low_kw)
    urgent_found = any(k in desc_lower for k in urgent_kw)
    standard_found = any(k in desc_lower for k in standard_kw)
    if urgent_found:
        priority = 'Urgent'
    elif standard_found:
        priority = 'Standard'
    elif low_found:
        priority = 'Low'
    else:
        # Default to Standard when unclear
        priority = 'Standard'

    # Build reason: one sentence citing specific words from the description
    if matched_words:
        cited = ", ".join(f"'{w}'" for w in matched_words[:3])
        reason = f"Mentions {cited} in the description."
    else:
        # No clear keyword match — use a concise fallback sentence
        excerpt = description[:80].replace('\n', ' ').strip()
        reason = f"No clear keywords found; excerpt: '{excerpt}'."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    try:
        with open(input_path, newline='', encoding='utf-8') as inf, \
             open(output_path, 'w', newline='', encoding='utf-8') as outf:
            reader = csv.DictReader(inf)
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                except Exception as e:
                    # On per-row error, write a placeholder and continue
                    sys.stderr.write(f"Row {i} classification error: {e}\n")
                    result = {
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Classification failed for this row.',
                        'flag': 'NEEDS_REVIEW',
                    }
                writer.writerow({k: result.get(k, '') for k in fieldnames})
    except FileNotFoundError:
        raise
    except Exception as e:
        # Bubble up unexpected errors after reporting
        sys.stderr.write(f"batch_classify error: {e}\n")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
