import csv
import sys
import argparse
import re
from typing import Dict, List, Tuple

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "hole in road", "road cavity", "sunken road"],
    "Flooding": ["flood", "waterlogged", "water logging", "standing water", "inundation", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp post", "light not working", "dark street", "broken light"],
    "Waste": ["garbage", "trash", "waste", "rubbish", "dumping", "litter", "overflowing bin", "dustbin"],
    "Noise": ["noise", "loud", "sound", "honking", "music", "construction noise", "disturbance"],
    "Road Damage": ["road damage", "cracked road", "broken road", "uneven road", "road broken", "damaged road", "crumbling"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "temple damage", "heritage site"],
    "Heat Hazard": ["heat", "hot", "temperature", "scorching", "heat wave", "extreme heat"],
    "Drain Blockage": ["drain", "blocked drain", "clogged drain", "drainage", "sewer", "gutter blocked"],
}

def classify_complaint(description: str) -> Dict[str, str]:
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Unable to classify: invalid or empty description",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    desc_stripped = description.strip()
    
    # Check for urgent keywords
    priority = "Standard"
    urgent_matched = []
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            urgent_matched.append(kw)
    
    # Classify category
    category_scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            category_scores[cat] = score
    
    if category_scores:
        sorted_cats = sorted(category_scores.items(), key=lambda x: (-x[1], x[0]))
        top_score = sorted_cats[0][1]
        top_categories = [cat for cat, score in sorted_cats if score == top_score]
        
        if len(top_categories) > 1:
            category = top_categories[0]
            flag = "NEEDS_REVIEW"
        else:
            category = top_categories[0]
            flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    # Generate reason citing specific words from description
    reason = generate_reason(desc_stripped, category, priority, urgent_matched)
    
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def generate_reason(description: str, category: str, priority: str, urgent_matched: List[str]) -> str:
    desc_lower = description.lower()
    
    matched_keywords = []
    if category in CATEGORY_KEYWORDS:
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in desc_lower:
                matched_keywords.append(kw)
    
    parts = []
    if matched_keywords:
        cited = ", ".join(f'"{kw}"' for kw in matched_keywords[:3])
        parts.append(f"complaint mentions {cited}")
    if urgent_matched:
        cited = ", ".join(f'"{kw}"' for kw in urgent_matched[:3])
        parts.append(f"urgent keywords {cited} present")
    
    if not parts:
        parts.append("no specific keywords matched")
    
    reason = f"Classified as {category} because {'; '.join(parts)}."
    return reason

def batch_classify(input_path: str, output_path: str) -> None:
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unable to read input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    if 'description' not in (rows[0] if rows else {}):
        print("Error: Input CSV must have a 'description' column", file=sys.stderr)
        sys.exit(1)
    
    output_rows = []
    for idx, row in enumerate(rows):
        desc = row.get('description', '')
        if not desc or not desc.strip():
            print(f"Warning: Row {idx} has missing or empty description, skipping", file=sys.stderr)
            continue
        try:
            result = classify_complaint(desc)
            output_rows.append(result)
        except Exception as e:
            print(f"Error processing row {idx}: {e}, skipping", file=sys.stderr)
            continue
    
    fieldnames = ['category', 'priority', 'reason', 'flag']
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Classify citizen complaints')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Classification complete. Results written to {args.output}")

if __name__ == '__main__':
    main()