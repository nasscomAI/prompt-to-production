"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def _extract_category(description: str) -> str:
    desc_lower = description.lower()
    
    # Simple heuristic matching for categories
    if "pothole" in desc_lower or "crater" in desc_lower or "road surface cracked" in desc_lower:
         # Need to differentiate between pothole and general road damage
         if "pothole" in desc_lower or "crater" in desc_lower:
            return "Pothole"
         return "Road Damage"
    elif "flood" in desc_lower or "water" in desc_lower and "drain" not in desc_lower:
        return "Flooding"
    elif "streetlight" in desc_lower or "light" in desc_lower or "dark" in desc_lower:
        return "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "dump" in desc_lower:
        return "Waste"
    elif "noise" in desc_lower or "music" in desc_lower or "loud" in desc_lower or "drilling" in desc_lower:
        return "Noise"
    elif "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower or "monument" in desc_lower:
        return "Heritage Damage"
    elif "heat" in desc_lower or "temperature" in desc_lower or "sun" in desc_lower or "melting" in desc_lower:
        return "Heat Hazard"
    elif "drain" in desc_lower or "block" in desc_lower:
        return "Drain Blockage"
    
    return "Other"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    if not description:
         return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # 1. Determine Category
    category = _extract_category(description)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority based on severity keywords
    priority = "Standard"
    matched_severity_keyword = None
    for keyword in SEVERITY_KEYWORDS:
        if re.search(rf"\b{keyword}\b", desc_lower):
            priority = "Urgent"
            matched_severity_keyword = keyword
            break
            
    if priority == "Standard" and category == "Other":
        priority = "Low"
        
    # 3. Formulate Reason
    reason = "N/A"
    if priority == "Urgent":
        reason = f"Classified as {category} with Urgent priority due to the presence of severity keyword '{matched_severity_keyword}'."
    elif category != "Other":
        reason = f"Classified as {category} based on description keywords."
    else:
         reason = "Could not confidently classify the complaint from the description."
         
    # Ensure category is strictly from allowed list (fallback check)
    if category not in ALLOWED_CATEGORIES:
         category = "Other"
         flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            results = []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                     # Log error and continue to next row to prevent crashing
                     print(f"Error processing row {row.get('complaint_id', 'UNKNOWN')}: {e}")
                     results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                     })
                     
        if results:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
                
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
