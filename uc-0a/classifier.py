"""
UC-0A — Complaint Classifier
Classifies citizen complaints into standardized categories with severity priority.
RICE Enforcement: category exactly from allowed list, priority based on severity keywords,
reason must cite specific words from description, flag set for ambiguous cases.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = {
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

ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    RICE Enforcement:
    - Category must be exactly one of the 10 allowed values
    - Priority must be Urgent if severity keywords present
    - Reason must cite specific words from description
    - Flag must be NEEDS_REVIEW if ambiguous, else blank
    """
    complaint_id = row.get("complaint_id", "unknown")
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Insufficient complaint text for classification.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Determine priority based on severity keywords
    has_severity = any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"
    
    # Use AI-guided classification based on description content
    # This is a simplified rule-based classifier for demonstration
    category, reason, needs_review = classify_by_keywords(description, description_lower)
    
    flag = "NEEDS_REVIEW" if needs_review else ""
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def classify_by_keywords(description: str, description_lower: str) -> tuple:
    """
    Classify complaint by keywords in the description.
    Returns: (category, reason, needs_review)
    """
    # Pothole detection
    if any(word in description_lower for word in ["pothole", "crater", "ditch", "pit"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['pothole', 'crater', 'ditch', 'pit'])}' indicating road surface damage."
        return "Pothole", reason, False
    
    # Flooding detection
    if any(word in description_lower for word in ["flood", "water", "stagnant water", "overflow", "waterlogged"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['flood', 'water', 'overflow', 'waterlogged'])}' indicating flooding."
        return "Flooding", reason, False
    
    # Streetlight detection
    if any(word in description_lower for word in ["light", "streetlight", "lamp", "dark", "streetlamp"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['light', 'streetlight', 'lamp', 'dark'])}' indicating lighting issue."
        return "Streetlight", reason, False
    
    # Waste detection
    if any(word in description_lower for word in ["waste", "garbage", "trash", "litter", "debris"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['waste', 'garbage', 'trash', 'debris'])}' indicating waste management issue."
        return "Waste", reason, False
    
    # Noise detection
    if any(word in description_lower for word in ["noise", "loud", "sound", "noise pollution", "honking"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['noise', 'loud', 'sound', 'honking'])}' indicating noise issue."
        return "Noise", reason, False
    
    # Road damage detection
    if any(word in description_lower for word in ["road", "pavement", "crack", "broken road", "damaged"]):
        if "pothole" not in description_lower:
            reason = f"Description mentions '{extract_keyword(description_lower, ['road', 'pavement', 'crack', 'damaged'])}' indicating road damage."
            return "Road Damage", reason, False
    
    # Heritage damage detection
    if any(word in description_lower for word in ["heritage", "monument", "historical", "temple", "mosque", "church"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['heritage', 'monument', 'historical', 'temple'])}' indicating heritage damage."
        return "Heritage Damage", reason, False
    
    # Heat hazard detection
    if any(word in description_lower for word in ["heat", "temperature", "hot", "scorching", "heat wave"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['heat', 'temperature', 'hot', 'scorching'])}' indicating heat hazard."
        return "Heat Hazard", reason, False
    
    # Drain blockage detection
    if any(word in description_lower for word in ["drain", "sewage", "blockage", "clogged", "drainage"]):
        reason = f"Description mentions '{extract_keyword(description_lower, ['drain', 'sewage', 'blockage', 'clogged'])}' indicating drain blockage."
        return "Drain Blockage", reason, False
    
    # Ambiguous case
    reason = f"Complaint description does not clearly indicate a specific category: '{description[:100]}...'"
    return "Other", reason, True


def extract_keyword(text: str, keywords: list) -> str:
    """Extract the first matching keyword from text."""
    for keyword in keywords:
        if keyword in text:
            return keyword
    return "unknown"


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: produce output even if some rows fail, preserve row order.
    """
    results = []
    error_count = 0
    success_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames or 'description' not in reader.fieldnames:
                print(f"Error: Input CSV must have 'description' column.", file=sys.stderr)
                return
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{row_num}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Failed to classify: {str(e)[:50]}",
                        "flag": "NEEDS_REVIEW"
                    })
                    print(f"Warning: Row {row_num} classification failed: {e}", file=sys.stderr)
        
        # Write output CSV
        output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Classification complete: {success_count} succeeded, {error_count} encountered errors.")
        print(f"Results written to {output_path}")
    
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during batch classification: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
