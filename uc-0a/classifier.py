"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def search_keywords(text: str, keywords: list) -> list:
    """
    Search for keywords in text. Enforce word boundaries for safety, 
    but allow common suffixes (like -s, -ed, -ing, -ised).
    """
    matched = []
    text_lower = text.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower == 'sun':
            pattern = r'\bsun\b'
        elif kw_lower == 'hospital':
            pattern = r'\bhospital(?:s|ised|ized)?\b'
        elif kw_lower == 'injury':
            pattern = r'\binjur(?:y|ed|ies)\b'
        elif kw_lower == 'collapse':
            pattern = r'\bcollaps(?:e|ed|ing|es)?\b'
        elif kw_lower == 'child':
            pattern = r'\bchild(?:ren|s)?\b'
        else:
            escaped_kw = re.escape(kw_lower)
            pattern = rf'\b{escaped_kw}(?:s|es|d|ed|ing)?\b'
            
        if re.search(pattern, text_lower):
            matched.append(kw)
    return matched


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Your RICE enforcement rules are reflected in this function's behaviour.
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '')
    
    if not description or description.strip() == '':
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # 1. Check for priority based on severity keywords
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_severity = search_keywords(description, severity_keywords)
    priority = 'Urgent' if matched_severity else 'Standard'
    
    # 2. Map category keywords in precedence order (specific first)
    category_map = {
        'Pothole': ['pothole'],
        'Flooding': ['flood', 'rainwater'],
        'Drain Blockage': ['stormwater drain', 'drainage', 'drain', 'manhole'],
        'Streetlight': ['streetlight', 'light', 'unlit', 'darkness'],
        'Heritage Damage': ['heritage', 'historic', 'ancient step well'],
        'Heat Hazard': ['melting', 'heat', 'temperature', 'heatwave', 'sun', 'burns'],
        'Noise': ['noise', 'drilling', 'engine', 'music', 'loud', 'amplifier'],
        'Road Damage': ['road collapsed', 'crater', 'road surface', 'buckled', 'subsidence', 'sinking', 'cracked', 'paving', 'road damage'],
        'Waste': ['garbage', 'waste', 'debris', 'trash', 'dead animal'],
    }
    
    matched_categories = []
    matched_kws = {}
    for cat, keywords in category_map.items():
        found = search_keywords(description, keywords)
        if found:
            matched_categories.append(cat)
            matched_kws[cat] = found
            
    # Ambiguity detection rules
    is_ambiguous = False
    ambiguity_reason = ""
    
    # If it contains both flood/rainwater and drain/drainage/stormwater drain/manhole
    has_flood = len(search_keywords(description, ['flood', 'rainwater'])) > 0
    has_drain = len(search_keywords(description, ['drain', 'drainage', 'stormwater drain', 'manhole'])) > 0
    if has_flood and has_drain:
        is_ambiguous = True
        ambiguity_reason = "Ambiguous: contains references to both Flooding and Drain Blockage"
        
    # If it contains heritage/historic and waste/garbage/trash
    has_heritage = len(search_keywords(description, ['heritage', 'historic', 'ancient step well'])) > 0
    has_waste = len(search_keywords(description, ['garbage', 'waste', 'trash', 'debris'])) > 0
    if has_heritage and has_waste:
        is_ambiguous = True
        ambiguity_reason = "Ambiguous: contains references to both Heritage and Waste"

    # If it contains heritage/historic and light/lights/streetlight
    has_light = len(search_keywords(description, ['light', 'unlit', 'darkness'])) > 0
    if has_heritage and has_light:
        is_ambiguous = True
        ambiguity_reason = "Ambiguous: contains references to both Heritage and Streetlight"
        
    # If it contains heritage/historic and road damage keywords
    has_road = len(search_keywords(description, ['road surface', 'paving', 'cobblestones', 'subsidence', 'crater'])) > 0
    if has_heritage and has_road:
        is_ambiguous = True
        ambiguity_reason = "Ambiguous: contains references to both Heritage and Road Damage"

    # If it contains heritage/historic and noise keywords
    has_noise = len(search_keywords(description, ['noise', 'music', 'amplifier', 'band'])) > 0
    if has_heritage and has_noise:
        is_ambiguous = True
        ambiguity_reason = "Ambiguous: contains references to both Heritage and Noise"

    # Assign category, flag, and build reasoning
    if not matched_categories:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        reason = "Unable to classify category from description alone."
    elif is_ambiguous:
        category = 'Other'
        flag = 'NEEDS_REVIEW'
        reason = ambiguity_reason + "."
    else:
        category = matched_categories[0]
        flag = ''
        
        cite_cat_kw = matched_kws[category][0]
        reason_parts = [f"Classified as {category} due to the word '{cite_cat_kw}' in description"]
        if priority == 'Urgent':
            cite_sev_kw = matched_severity[0]
            reason_parts.append(f"priority set to Urgent because of keyword '{cite_sev_kw}'")
        else:
            reason_parts.append("priority set to Standard as no severity keywords were found")
        reason = ", and ".join(reason_parts) + "."

    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row: {row}. Error: {e}")
                    results.append({
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f"Error during classification: {e}",
                        'flag': 'NEEDS_REVIEW'
                    })
    except Exception as e:
        print(f"Failed to read input CSV file {input_path}: {e}")
        return False
        
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output CSV file {output_path}: {e}")
        return False
        
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
