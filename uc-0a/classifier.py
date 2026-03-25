"""
UC-0A — Complaint Classifier
Rewritten based on RICE -> agents.md -> skills.md constraints.
"""
import argparse
import csv
import re

CATEGORY_KEYWORDS = {
    'Pothole': [r'\bpotholes?\b'],
    'Flooding': [r'\bflood(?:ing|s|ed)?\b', r'\bwater\b', r'\brain\b'],
    'Streetlight': [r'\bstreetlights?\b', r'\blights? out\b', r'\bdark(?:ness)?\b'],
    'Waste': [r'\bwaste\b', r'\bgarbage\b', r'\btrash\b', r'\bdump(?:ing)?\b'],
    'Noise': [r'\bnoise\b', r'\bmusic\b', r'\bloud\b'],
    'Road Damage': [r'\broad\s+(?:surface|damage)\b', r'\bcracks?\b', r'\bsinking\b'],
    'Heritage Damage': [r'\bheritage\b', r'\bmonument\b'],
    'Heat Hazard': [r'\bheat(?:wave)?\b'],
    'Drain Blockage': [r'\bdrains?\b', r'\bmanholes?\b', r'\bblock(?:ed|age)?\b']
}

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def get_sentences(text: str) -> list:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    return sentences

def classify_complaint(row: dict) -> dict:
    description = str(row.get('description', ''))
    desc_lower = description.lower()
    
    # 1. PRIORITY
    priority = 'Standard'
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf'\b{kw}\b', desc_lower):
            matched_severity.append(kw)
    
    if matched_severity:
        priority = 'Urgent'
        
    # 2. CATEGORY
    matched_categories = set()
    matched_cat_keywords = []
    
    for cat, patterns in CATEGORY_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, desc_lower):
                matched_categories.add(cat)
                word_clean = pat.replace(r'\b', '').replace(r'(?:', '(').split('(')[0].replace('?', '').replace('\\s+', ' ').replace('\\', '')
                matched_cat_keywords.append(word_clean)
                
    category = "Other"
    flag = ""
    trigger_words = []
    
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        trigger_words = matched_cat_keywords
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        trigger_words = matched_cat_keywords
    else:
        # None matched
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 3. REASON: exactly one sentence & cite specific words
    sentences = get_sentences(description)
    reason = "No specific reason could be identified."
    
    # Look for the sentence containing the trigger or severity keywords
    target_sentence = sentences[0] if sentences else ""
    cited_w = None
    
    all_keywords = matched_severity + trigger_words
    
    if all_keywords:
        for s in sentences:
            s_low = s.lower()
            found = [kw for kw in all_keywords if kw in s_low]
            if found:
                target_sentence = s
                cited_w = found[0]
                break
                
    if target_sentence:
        if cited_w:
            reason = f'Due to keyword "{cited_w}", {target_sentence}.'
        else:
            reason = f'Based on description, {target_sentence}.'
            
    # Ambiguous reasoning fallback
    if flag == "NEEDS_REVIEW":
        if matched_severity:
            reason = f'Genuinely ambiguous category but Urgent priority assigned citing "{matched_severity[0]}".'
        elif len(matched_categories) > 1:
            cats = " and ".join(list(matched_categories))
            reason = f'Genuinely ambiguous because it involves multiple issues like {cats} citing "{trigger_words[0]}".'
        else:
            reason = f'Genuinely ambiguous description with no recognizable categorized keywords from the allowed list.'

    # Post processing constraint: Reason MUST be exactly one sentence.
    if "." not in reason:
        reason += "."
        
    # Normalize ending
    reason = reason.split('.')[0] + "."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            reader = csv.DictReader(f_in)
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                if not row or not row.get('complaint_id'):
                    continue
                try:
                    res = classify_complaint(row)
                    writer.writerow({
                        'complaint_id': res['complaint_id'],
                        'category': res['category'],
                        'priority': res['priority'],
                        'reason': res['reason'],
                        'flag': res['flag']
                    })
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    writer.writerow({
                        'complaint_id': row.get('complaint_id', 'UNKNOWN'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Row processing failed.',
                        'flag': 'NEEDS_REVIEW'
                    })
    except Exception as e:
        print(f"Critical error in batch processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
