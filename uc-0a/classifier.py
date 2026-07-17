"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md specifications.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple


# Category keywords mapping (from README.md classification schema)
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "road hole", "road damage"],
    "Flooding": ["flood", "flooding", "flooded", "floods", "water logging", "waterlogged", "inundated", "draining", "drainage onto", "rainwater", "channel rainwater"],
    "Streetlight": ["streetlight", "street light", "streetlights out", "lamp post", "light not working", "no light", "substation", "darkness", "power outage", "electricity", "lights out", "unlit", "wiring theft", "wiring"],
    "Waste": ["waste", "garbage", "trash", "rubbish", "litter", "dump", "sewage", "overflowing", "dead animal", "not removed", "post-market waste"],
    "Noise": ["noise", "loud", "noisy", "disturbance", "music", "construction noise", "band", "amplifier", "amplifiers", "wedding band", "playing", "decibel", "past midnight", "drilling", "construction drilling", "idling", "engines on"],
    "Road Damage": ["road damage", "cracked road", "broken road", "road repair", "asphalt", "footpath", "broken", "sinking", "buckled", "subsided", "road surface", "paving", "manhole", "missing", "collapsed", "crater", "dead trees", "split branches", "fall risk", "trees affected"],
    "Heritage Damage": ["heritage", "historic", "monument", "ancient", "heritage site", "cobblestone", "tram road", "heritage zone", "heritage stone", "heritage building", "heritage residential", "heritage precinct"],
    "Heat Hazard": ["heat", "extreme heat", "heat wave", "hot", "sun stroke", "heat stroke", "melting", "dangerous temperatures", "unbearable", "52°C", "44°C", "45°C", "burns on contact", "temperature reads", "temperature"],
    "Drain Blockage": ["blocked drain", "clogged drain", "sewer", "storm drain", "draining", "drain blocked", "stormwater drain", "drain completely blocked", "drain blocked"],
}

# Severity keywords that trigger Urgent priority (from README.md)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

# Allowed categories (from README.md)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]


def extract_keywords(text: str) -> List[str]:
    """Extract words from text for matching purposes."""
    return re.findall(r'\b\w+\b', text.lower())


def find_matching_keywords(description: str, keyword_list: List[str]) -> List[str]:
    """Find which keywords from a list appear in the description."""
    desc_lower = description.lower()
    return [kw for kw in keyword_list if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)]


def classify_category(description: str) -> Tuple[str, bool]:
    """
    Classify complaint into one of the allowed categories.
    Returns: (category, is_ambiguous)
    """
    desc_lower = description.lower()
    matches = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                matches.append(category)
                break
    
    if len(matches) == 1:
        return matches[0], False
    elif len(matches) > 1:
        # Multiple matches - disambiguate based on context
        # Priority order: Heritage Damage > Road Damage > Pothole > Drain Blockage > Streetlight > others
        # Heritage complaints often involve infrastructure elements
        if "Heritage Damage" in matches:
            return "Heritage Damage", False
        elif "Road Damage" in matches:
            return "Road Damage", False
        elif "Pothole" in matches:
            return "Pothole", False
        elif "Drain Blockage" in matches:
            return "Drain Blockage", False
        elif "Streetlight" in matches:
            return "Streetlight", False
        return matches[0], True
    else:
        return "Other", True


def classify_priority(description: str) -> str:
    """
    Determine priority based on severity keywords.
    Returns: Urgent, Standard, or Low
    """
    found_severity = find_matching_keywords(description, SEVERITY_KEYWORDS)
    if found_severity:
        return "Urgent"
    return "Standard"


def generate_reason(description: str, category: str) -> str:
    """
    Generate a reason citing specific words from the description.
    """
    desc_lower = description.lower()
    
    # Find category-specific keywords mentioned in description
    if category in CATEGORY_KEYWORDS:
        category_keywords = CATEGORY_KEYWORDS[category]
        mentioned = [kw for kw in category_keywords if kw in desc_lower]
        if mentioned:
            return f"Complaint mentions '{', '.join(mentioned[:3])}' indicating {category} issue."
    
    # Fallback: use severity keywords if present
    severity_found = find_matching_keywords(description, SEVERITY_KEYWORDS)
    if severity_found:
        return f"Complaint mentions '{', '.join(severity_found[:3])}' requiring urgent attention."
    
    # Generic reason
    return f"Classification based on description content indicating {category} type complaint."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Rules from agents.md:
    - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    - Priority must be Urgent if description contains: injury, child, school, hospital,
      ambulance, fire, hazard, fell, collapse
    - Every output row must include a reason field citing specific words
    - If category cannot be determined, output category: Other and flag: NEEDS_REVIEW
    """
    description = row.get("description", "")
    
    # Classify category
    category, is_ambiguous = classify_category(description)
    
    # Classify priority
    priority = classify_priority(description)
    
    # Generate reason
    reason = generate_reason(description, category)
    
    # Set flag if ambiguous
    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    
    # Ensure category is in allowed list
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Rules from skills.md:
    - For any row that fails classification, apply fallback (Other + NEEDS_REVIEW)
      and continue processing remaining rows.
    """
    results = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for i, row in enumerate(reader, 1):
                try:
                    # Check if required fields exist
                    if not row.get("description"):
                        results.append({
                            "complaint_id": row.get("complaint_id", str(i)),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "No description provided for classification.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                    
                    # Classify the complaint
                    classified = classify_complaint(row)
                    results.append(classified)
                    
                except Exception as e:
                    # Fallback for any errors during classification
                    results.append({
                        "complaint_id": row.get("complaint_id", str(i)),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error during classification: {str(e)[:50]}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Write results to output CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return
    
    print(f"Classified {len(results)} complaints. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)