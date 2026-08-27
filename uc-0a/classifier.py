"""
UC-0A classifier.py — Civic Complaint Classifier
Classifies citizen complaints into categories and priority levels.
"""
import csv
import argparse
from typing import Dict, List, Tuple

# Fixed taxonomy - exactly these 10 categories, no variations
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
    "Other"
]

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]


def detect_severity_keywords(description: str) -> Tuple[bool, List[str]]:
    """
    Detect if any severity keywords are present in the description.
    Returns: (has_severity, list_of_matched_keywords)
    """
    if not description:
        return False, []
    
    desc_lower = description.lower()
    matched = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    
    return len(matched) > 0, matched


def map_to_category(description: str) -> str:
    """
    Map complaint description to one of the 10 allowed categories.
    Returns exact category name from ALLOWED_CATEGORIES or 'Other'.
    """
    if not description:
        return "Other"
    
    desc_lower = description.lower()
    
    # Category keyword mapping
    if "pothole" in desc_lower:
        return "Pothole"
    
    if "flood" in desc_lower or "flooded" in desc_lower or "water" in desc_lower and "rain" in desc_lower:
        return "Flooding"
    
    if "streetlight" in desc_lower or "street light" in desc_lower or ("light" in desc_lower and ("out" in desc_lower or "dark" in desc_lower or "flickering" in desc_lower or "sparking" in desc_lower)):
        return "Streetlight"
    
    if "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "bin" in desc_lower and "overflow" in desc_lower:
        return "Waste"
    
    if "noise" in desc_lower or "music" in desc_lower and ("loud" in desc_lower or "midnight" in desc_lower or "night" in desc_lower):
        return "Noise"
    
    if "road" in desc_lower and ("crack" in desc_lower or "sinking" in desc_lower or "damage" in desc_lower or "surface" in desc_lower):
        return "Road Damage"
    
    if "heritage" in desc_lower or ("old city" in desc_lower or "historical" in desc_lower):
        return "Heritage Damage"
    
    if "heat" in desc_lower and "hazard" in desc_lower:
        return "Heat Hazard"
    
    if "drain" in desc_lower and "block" in desc_lower:
        return "Drain Blockage"
    
    if "manhole" in desc_lower and "missing" in desc_lower:
        return "Road Damage"  # Missing manhole is road damage
    
    if "animal" in desc_lower and "dead" in desc_lower:
        return "Waste"  # Dead animal is waste management issue
    
    if "footpath" in desc_lower or "tiles" in desc_lower and "broken" in desc_lower:
        return "Road Damage"  # Broken footpath is road damage
    
    if "bridge" in desc_lower and "flood" in desc_lower:
        return "Flooding"
    
    if "bulk waste" in desc_lower or "dumped" in desc_lower:
        return "Waste"
    
    # If no clear match, return Other
    return "Other"


def generate_reason(description: str, category: str, priority: str, severity_keywords: List[str]) -> str:
    """
    Generate a reason citing specific words from the description.
    """
    if not description:
        return "Insufficient information in complaint description"
    
    desc_lower = description.lower()
    reason_parts = []
    
    # Explain category
    if category == "Pothole" and "pothole" in desc_lower:
        reason_parts.append("description mentions 'pothole'")
    elif category == "Flooding" and "flood" in desc_lower:
        reason_parts.append("description mentions 'flooded'")
    elif category == "Streetlight" and ("light" in desc_lower or "streetlight" in desc_lower):
        reason_parts.append("description mentions streetlight issues")
    elif category == "Waste" and ("garbage" in desc_lower or "waste" in desc_lower):
        reason_parts.append("description mentions waste/garbage")
    elif category == "Noise" and "noise" in desc_lower or "music" in desc_lower:
        reason_parts.append("description mentions noise complaint")
    elif category == "Road Damage":
        reason_parts.append("description mentions road surface issues")
    elif category == "Heritage Damage":
        reason_parts.append("description mentions heritage area")
    elif category == "Drain Blockage":
        reason_parts.append("description mentions blocked drain")
    else:
        reason_parts.append(f"classified as {category} based on description content")
    
    # Explain priority
    if severity_keywords:
        kw_str = "', '".join(severity_keywords)
        reason_parts.append(f"marked Urgent due to severity keywords: '{kw_str}'")
    elif priority == "Standard":
        reason_parts.append("no severity keywords, marked Standard priority")
    elif priority == "Low":
        reason_parts.append("no severity keywords, low urgency")
    
    return "; ".join(reason_parts)


def classify_complaint(complaint: Dict) -> Dict:
    """
    Classify a single complaint.
    Returns: {category, priority, reason, flag}
    """
    description = complaint.get('description', '')
    days_open = int(complaint.get('days_open', 0))
    
    # Detect severity keywords
    has_severity, severity_kws = detect_severity_keywords(description)
    
    # Map to category
    category = map_to_category(description)
    
    # Determine priority
    if has_severity:
        priority = "Urgent"
    elif days_open > 15:
        priority = "Standard"  # Been open a while but no severity
    else:
        priority = "Standard"  # Default
    
    # Generate reason
    reason = generate_reason(description, category, priority, severity_kws)
    
    # Set flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each complaint, write output CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            complaints = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading input file: {str(e)}")
    
    # Classify each complaint
    results = []
    for complaint in complaints:
        classification = classify_complaint(complaint)
        results.append({
            'complaint_id': complaint['complaint_id'],
            'category': classification['category'],
            'priority': classification['priority'],
            'reason': classification['reason'],
            'flag': classification['flag']
        })
    
    # Write output
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✓ Classified {len(results)} complaints")
        print(f"✓ Output written to {output_path}")
        
        # Summary statistics
        urgent_count = sum(1 for r in results if r['priority'] == 'Urgent')
        needs_review = sum(1 for r in results if r['flag'] == 'NEEDS_REVIEW')
        
        print(f"\nSummary:")
        print(f"  Urgent priority: {urgent_count}/{len(results)}")
        print(f"  Needs review: {needs_review}/{len(results)}")
        
    except Exception as e:
        raise Exception(f"Error writing output file: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Classify civic complaints')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Civic Complaint Classifier - UC-0A")
    print("=" * 70)
    print(f"\nInput: {args.input}")
    print(f"Output: {args.output}\n")
    
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()
