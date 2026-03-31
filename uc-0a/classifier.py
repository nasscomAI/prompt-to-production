"""
UC-0A — Complaint Classifier
Implements complaint classification following RICE enforcement rules from agents.md.
"""
import argparse
import csv
import re

# Allowed categories — exact strings only
CATEGORIES = {
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
}

# Severity keywords that trigger Urgent priority
SEVERITY_KEYWORDS = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}

# Keyword-to-category mappings for classification
CATEGORY_KEYWORDS = {
    "Pothole": {"pothole", "hole", "pit", "crater", "dent", "depression"},
    "Flooding": {"flood", "water", "inundation", "submerged", "waterlog"},
    "Streetlight": {"light", "lamp", "streetlight", "street light", "illumination", "dark"},
    "Waste": {"garbage", "trash", "waste", "litter", "rubbish", "debris", "dump"},
    "Noise": {"noise", "sound", "loud", "music", "barking", "honking"},
    "Road Damage": {"crack", "damaged", "pavement", "asphalt", "surface", "broken road"},
    "Heritage Damage": {"heritage", "monument", "historical", "ancient", "temple", "mosque", "church", "historic site"},
    "Heat Hazard": {"heat", "heatwave", "temperature", "hot", "scorching", "warm"},
    "Drain Blockage": {"drain", "blockage", "clogged", "sewage", "blockage", "overflow"}
}


def extract_keywords_from_description(description: str) -> set:
    """Extract lowercase words from description for matching."""
    if not description:
        return set()
    words = re.findall(r'\b\w+\b', description.lower())
    return set(words)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Args:
        row: dict with keys complaint_id and description
        
    Returns: 
        dict with keys: category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "") or ""
    
    # Extract keywords for matching
    keywords = extract_keywords_from_description(description)
    
    # Determine category by keyword matching
    category = "Other"
    best_match_count = 0
    
    for cat, cat_keywords in CATEGORY_KEYWORDS.items():
        match_count = len(keywords & cat_keywords)
        if match_count > best_match_count:
            category = cat
            best_match_count = match_count
    
    # Set flag if no confident match was found
    flag = "NEEDS_REVIEW" if best_match_count == 0 and description else ""
    
    # Determine priority: Urgent if severity keywords present
    has_severity = any(keyword in keywords for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"
    
    # Generate reason: cite specific words from description that led to classification
    reason = generate_reason(description, category, keywords)
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def generate_reason(description: str, category: str, keywords: set) -> str:
    """
    Generate a single-sentence reason citing specific words from the description.
    
    Args:
        description: the original complaint text
        category: the assigned category
        keywords: set of keyword tokens from description
        
    Returns:
        A single sentence reason
    """
    if not description:
        return "Cannot determine reason — description is empty."
    
    if category == "Other":
        return f"Complaint contains: {description[:50]}... but does not clearly match any category."
    
    # Find relevant keywords that match this category
    cat_keywords = CATEGORY_KEYWORDS.get(category, set())
    matching_keywords = keywords & cat_keywords
    
    if matching_keywords:
        cited_word = next(iter(matching_keywords))
        # Find the cited word in original description (case-insensitive)
        pattern = re.compile(re.escape(cited_word), re.IGNORECASE)
        match = pattern.search(description)
        if match:
            cited = match.group()
            return f"Complaint mentions '{cited}', indicating {category}."
    
    return f"Complaint description indicates {category}."


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    Args:
        input_path: path to input CSV (must have complaint_id, description columns)
        output_path: path to write output CSV
    """
    try:
        # Read input CSV
        rows = []
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "description" not in reader.fieldnames:
                raise ValueError("Input CSV must have a 'description' column")
            rows = list(reader)
        
        if not rows:
            raise ValueError(f"Input CSV is empty: {input_path}")
        
        # Classify each row
        results = []
        for row in rows:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                # On error, mark row as needing review
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error during classification: {str(e)[:50]}",
                    "flag": "NEEDS_REVIEW"
                })
        
        # Write output CSV
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise RuntimeError(f"Error during batch classification: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
