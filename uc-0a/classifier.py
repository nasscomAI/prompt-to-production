import csv
import argparse
import os
import re

# Classification Schema Constants
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row):
    """
    Transforms a single citizen complaint row into a structured classification.
    Skill defined in skills.md.
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Priority (Severity blindness check)
    priority = "Standard"
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif "noise" in description or "waste" in description:
        priority = "Low"
    
    # 2. Determine Category (Taxonomy check)
    category = "Other"
    flag = ""
    
    # Simple rule-based mapping for demonstration
    mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "light": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "road": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage"
    }
    
    found_categories = [cat for key, cat in mapping.items() if key in description]
    
    if len(found_categories) == 1:
        category = found_categories[0]
    elif len(found_categories) > 1:
        # Ambiguous case: False confidence check
        category = found_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        # Check for ambiguity if nothing found
        if description.strip():
            flag = "NEEDS_REVIEW"
            
    # 3. Generate Reason (Missing justification check)
    # Finding the specific word cited
    cited_word = next((kw for kw in SEVERITY_KEYWORDS if kw in description), None)
    if not cited_word:
        cited_word = next((key for key in mapping.keys() if key in description), "complaint")
    
    reason = f"The issue is classified as {category} due to the mention of '{cited_word}' in the description."
    
    # Final taxonomy validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path, output_path):
    """
    Orchestrates the classification of multiple complaints from CSV.
    Skill defined in skills.md.
    """
    if not os.path.exists(input_path):
        print(f"UC-0A Fix [failure mode]: Input file missing → Aborted")
        return

    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                classification = classify_complaint(row)
                
                # Validation against failure modes
                if classification["category"] not in ALLOWED_CATEGORIES:
                    raise ValueError(f"Taxonomy drift detected: {classification['category']} not in allowed list")
                
                if not classification["reason"] or "." not in classification["reason"]:
                    raise ValueError("Missing or invalid justification detected")
                
                # Merge original row with classification
                row.update(classification)
                results.append(row)
                
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            if not results:
                return
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Classification completed. Results written to {output_path}")

    except Exception as e:
        print(f"UC-0A Fix [failure mode]: Processing failed → {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Complaint Classifier for UC-0A")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()
