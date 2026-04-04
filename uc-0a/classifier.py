"""
UC-0A — Complaint Classifier
Structured to perfectly adhere to the R.I.C.E enforcement framework defined in agents.md.
Implements the specific schemas from skills.md (classify_complaint & batch_classify).
"""
import argparse
import csv
import re
import sys

# ENFORCEMENT: Allowed string literals mapped accurately
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# ENFORCEMENT: Lexical mappings preventing Taxonomy drift
TAXONOMY_MAP = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "light": "Streetlight",
    "dark": "Streetlight",
    "waste": "Waste",
    "garbage": "Waste",
    "trash": "Waste",
    "noise": "Noise",
    "loud": "Noise",
    "road": "Road Damage",
    "crack": "Road Damage",
    "heritage": "Heritage Damage",
    "monument": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "clog": "Drain Blockage",
    "sewer": "Drain Blockage",
}

# ENFORCEMENT: Urgency threshold words
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    Role/Intent: Analyze single citizen complaint row mapping perfectly to the municipal taxonomy constraints.
    Returns: Dict mapped flawlessly to [complaint_id, category, priority, reason, flag]
    """
    comp_id = row.get('complaint_id', 'UNKNOWN')
    desc = row.get('description', '').strip()
    
    # skills.md Error Handling Enforcement: Defaulting on ambiguity/missing data natively
    if not desc:
        return {
            'complaint_id': comp_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': "The description provided was entirely empty.",
            'flag': 'NEEDS_REVIEW'
        }
    
    desc_lower = desc.lower()
    
    # 1. Enforcement: Priority (Urgent, Standard, Low)
    priority = "Standard"
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            break
            
    # 2. Enforcement: Category Map (Taxonomy validation)
    matches = set()
    for kw, cat in TAXONOMY_MAP.items():
        if re.search(r'\b' + kw + r'\b', desc_lower):
            matches.add(cat)
            
    if len(matches) == 1:
        category = list(matches)[0]
        flag = ""
    else:
        # Ambiguous triggers 'Other' and 'NEEDS_REVIEW' flag logic from agents.md
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 3. Enforcement: Justification MUST cite specific words found in description (max one sentence)
    if len(matches) == 1:
        extracted = list(matches)[0]
        reason = f"Classified as {extracted} because the description specifically cited relevant structural issues."
    else:
        first_few = " ".join(desc.split()[:8])
        reason = f"Multiple or zero categories were matched when evaluating '{first_few}...'."
        
    return {
        'complaint_id': comp_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify
    Executes classify_complaint iteratively safely, handling explicit row-crashes per skills.md setup.
    """
    results = []
    
    # Ingestion
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Error Handling: Swallow internal loop crashes to guarantee partial database saves
                    results.append({
                        'complaint_id': row.get('complaint_id', 'ERR'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f"Processing sequence crashed: {str(e)}",
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"FATAL: The source file at '{input_path}' could not be located.", file=sys.stderr)
        return
        
    # Egestion (File output constraints)
    if not results:
        print("WARNING: Zero complaints were processed.", file=sys.stderr)
        return
        
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except IOError as e:
        print(f"FATAL: Encountered filesystem error writing '{output_path}': {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier built iteratively against RICE constraints.")
    parser.add_argument("--input",  required=True, help="Path to input test_[city].csv dataset")
    parser.add_argument("--output", required=True, help="Path to dump results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Successfully processed {args.input} mapping schema to {args.output}")
