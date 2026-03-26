"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Priority check
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_urgent = [kw for kw in urgent_keywords if kw in desc]
    priority = 'Urgent' if matched_urgent else 'Standard'
    
    # Category definitions
    cat_matches = {}
    if 'pothole' in desc:
        cat_matches['pothole'] = 'Pothole'
    if 'flood' in desc:
        cat_matches['flood'] = 'Flooding'
    if 'streetlight' in desc or 'lights' in desc or 'dark' in desc:
        if 'streetlight' in desc:
            cat_matches['streetlight'] = 'Streetlight'
        elif 'lights' in desc:
            cat_matches['lights'] = 'Streetlight'
        elif 'dark' in desc:
            cat_matches['dark'] = 'Streetlight'
    if 'waste' in desc or 'garbage' in desc or 'animal' in desc or 'bin' in desc:
        if 'waste' in desc:
            cat_matches['waste'] = 'Waste'
        elif 'garbage' in desc:
            cat_matches['garbage'] = 'Waste'
        elif 'animal' in desc:
            cat_matches['animal'] = 'Waste'
        elif 'bin' in desc:
            cat_matches['bin'] = 'Waste'
    if 'music' in desc or 'noise' in desc:
        cat_matches['music' if 'music' in desc else 'noise'] = 'Noise'
    if 'road surface' in desc or 'footpath' in desc or 'crack' in desc or 'sink' in desc:
        cat_matches['footpath' if 'footpath' in desc else ('road surface' if 'road surface' in desc else 'crack')] = 'Road Damage'
    if 'heritage' in desc:
        cat_matches['heritage'] = 'Heritage Damage'
    if 'heat' in desc:
        cat_matches['heat'] = 'Heat Hazard'
    if 'drain' in desc or 'manhole' in desc:
        cat_matches['drain' if 'drain' in desc else 'manhole'] = 'Drain Blockage'

    # Determine unique categories identified
    distinct_categories = list(set(cat_matches.values()))
    
    flag = ''
    matched_cat_word = 'None'
    if len(distinct_categories) == 0:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
    elif len(distinct_categories) == 1:
        category = distinct_categories[0]
        for word, cat in cat_matches.items():
            if cat == category:
                matched_cat_word = word
                break
    else:
        # Ambiguous categories
        category = 'Other'
        flag = 'NEEDS_REVIEW'

    # Construct exactly one sentence for the reason field
    if priority == 'Urgent':
        urgent_word = matched_urgent[0]
        if flag == 'NEEDS_REVIEW':
            if len(distinct_categories) == 0:
                reason = f"Priority is Urgent due to '{urgent_word}' but category is unknown."
            else:
                reason = f"Priority is Urgent due to '{urgent_word}' but category is ambiguous."
        else:
            reason = f"Classified as {category} based on '{matched_cat_word}' and marked Urgent due to '{urgent_word}'."
    else:
        if flag == 'NEEDS_REVIEW':
            if len(distinct_categories) == 0:
                reason = "Category is unknown because no keywords matched."
            else:
                reason = "Category is ambiguous because multiple keywords matched."
        else:
            reason = f"Classified as {category} based on the word '{matched_cat_word}'."

    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                if not row.get('description'):
                    row['category'] = 'Other'
                    row['priority'] = 'Low'
                    row['reason'] = 'Missing description.'
                    row['flag'] = 'NEEDS_REVIEW'
                    writer.writerow(row)
                    continue

                classification = classify_complaint(row)
                row.update(classification)
                writer.writerow(row)
            except Exception as e:
                # Must not crash on bad rows
                row['category'] = 'Other'
                row['flag'] = 'NEEDS_REVIEW'
                row['reason'] = f"Error: {e}"
                writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
