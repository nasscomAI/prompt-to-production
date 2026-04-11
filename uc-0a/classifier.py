"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    category = "Other"
    priority = "Standard"
    flag = ""
    reason = ""
    
    # Severity check
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    found_severity = None
    for kw in severity_keywords:
        if kw in desc:
            priority = "Urgent"
            found_severity = kw
            break
            
    # Category Classification rules
    cats = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "lights out": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "dead animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "crack": "Road Damage",
        "manhole": "Road Damage",
        "footpath": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain block": "Drain Blockage",
        "drainage": "Drain Blockage"
    }

    found_cats = []
    found_category_words = []

    # Category priority tiebreaker — more specific categories override generic ones
    # e.g. Heritage Damage > Streetlight when "heritage street, lights out"
    CATEGORY_PRIORITY = [
        "Heritage Damage", "Heat Hazard", "Drain Blockage",
        "Pothole", "Flooding", "Road Damage",
        "Waste", "Noise", "Streetlight", "Other"
    ]

    # Try exact overrides first
    if 'flooded' in desc and 'drain blocked' in desc:
        found_cats.append('Drain Blockage')
        found_category_words.append('drain blocked')
    else:
        for kw, cat in cats.items():
            if kw in desc:
                if cat not in found_cats:
                    found_cats.append(cat)
                    found_category_words.append(kw)

    if len(found_cats) == 1:
        category = found_cats[0]
        cat_word = found_category_words[0]
    elif len(found_cats) > 1:
        # Pick the highest-priority category instead of flagging NEEDS_REVIEW
        for preferred in CATEGORY_PRIORITY:
            if preferred in found_cats:
                idx = found_cats.index(preferred)
                category = preferred
                cat_word = found_category_words[idx]
                flag = ""
                break
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
            cat_word = "multiple conflicting terms"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cat_word = "no clear matching terms"

    # Construct one sentence for reason citing specific description words
    if priority == "Urgent":
        reason = f"Classified as {category} with Urgent priority due to quoting '{cat_word}' and '{found_severity}' from the description."
    else:
        reason = f"Classified as {category} with Standard priority due to citing '{cat_word}' from the description."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            if not fields:
                fields = []
            rows = list(reader)
            
        out_fields = fields + ['category', 'priority', 'reason', 'flag']
        seen = set()
        out_fields = [x for x in out_fields if not (x in seen or seen.add(x))]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            for row in rows:
                try:
                    res = classify_complaint(row)
                    for k in ['category', 'priority', 'reason', 'flag']:
                        row[k] = res.get(k, '')
                    writer.writerow(row)
                except Exception as e:
                    row['flag'] = 'ERROR'
                    row['reason'] = f"Exception during classification: {str(e)}"
                    writer.writerow(row)
    except Exception as e:
        print(f"Critical failure during batch operation: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
