"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re # Import regex for more flexible keyword matching and reason extraction
from typing import Dict, Any, List

# Define the Classification Schema directly within the script for clarity
# In a real application, this might come from a config file or a dedicated module.
CLASSIFICATION_SCHEMA = {
    "allowed_categories": [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ],
    "severity_keywords": [
        "injury", "child", "school", "hospital", "ambulance", "fire", 
        "hazard", "fell", "collapse", "risk" # Added 'risk' as it's implied by 'at risk' from sample
    ],
    # Keywords for category matching - prioritize more specific matches first
    "category_keywords": {
        "Pothole": ["pothole"],
        "Flooding": ["flooded", "standing in water", "inaccessible"],
        "Streetlight": ["streetlight", "lights out", "dark at night", "flickering", "sparking"],
        "Waste": ["garbage bins", "bulk waste", "dead animal", "smell"],
        "Noise": ["music past midnight", "noise complaint", "loud music"],
        "Road Damage": ["road surface cracked", "sinking", "manhole cover missing", "road damage"],
        "Drain Blockage": ["drain blocked", "clogged drain"], # Specific from text
        # "Heritage Damage": [], # No explicit keywords in sample, would need to be defined
        # "Heat Hazard": [], # No explicit keywords in sample, would need to be defined
    }
}


def classify_complaint(row: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a single complaint row based on the strict schema and enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "N/A")
    raw_description = row.get("description", "")
    description_lower = raw_description.lower()

    category = "Other" # Default as per enforcement rule
    priority = "Standard" # Default as per enforcement rule
    reason = "Description did not clearly match any specific category." # Default reason
    flag = "" # Default flag

    if not raw_description:
        flag = "Null Data - Missing Description Text"
        category = "Other"
        reason = "No description provided for classification."
        priority = "Low" # If no description, cannot be urgent.
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }

    # --- Enforcement Rule: Priority must be Urgent if severity keywords present ---
    matched_severity_keywords = []
    for keyword in schema["severity_keywords"]:
        if keyword in description_lower:
            matched_severity_keywords.append(keyword)
            # Use 'risk' as a more general trigger, but report the exact found words
            if keyword == "risk" and "at risk" in description_lower:
                 matched_severity_keywords = ["at risk"] # Refine to matched phrase
            priority = "Urgent"
            break # Once urgent, no need to check further

    # --- Enforcement Rule: Category must be exact strings only ---
    # --- Enforcement Rule: Reason must cite specific words from description ---
    matched_category_keyword = None
    for allowed_cat, keywords in schema["category_keywords"].items():
        for keyword in keywords:
            if keyword in description_lower:
                category = allowed_cat
                matched_category_keyword = keyword
                
                # Try to extract the phrase from the original description for the reason
                # This makes the reason more specific and directly citing
                match = re.search(r'\b' + re.escape(keyword) + r'\b', raw_description, re.IGNORECASE)
                if match:
                    reason = f"Classification based on phrase: '{match.group(0)}'."
                else: # Fallback if regex fails for some reason
                    reason = f"Classification based on keyword: '{keyword}'."
                
                break # Matched a category, move to next complaint
        if category != "Other":
            break # Break outer loop if category found

    # Handle categories without explicit keywords in schema (Heritage Damage, Heat Hazard)
    # This section would be for more advanced AI logic, but for simulation, we'll keep it simple
    # For now, if no other category matches, it remains "Other"

    # --- Enforcement Rule: Flag NEEDS_REVIEW or blank ---
    # Set flag to NEEDS_REVIEW if category is 'Other' and description is not null,
    # or if priority is Urgent but no specific severity keyword was found (ambiguity)
    # The ambiguity here is if the *simulated* logic can't confidently classify.
    if category == "Other" and raw_description:
        flag = "NEEDS_REVIEW"
        reason = "Description did not clearly match any defined category, defaulting to 'Other'."
    
    # If priority is Urgent, make sure the reason mentions the severity aspect
    if priority == "Urgent" and matched_severity_keywords and "Classification based on phrase" in reason:
        reason = f"{reason} Severity detected by: '{', '.join(matched_severity_keywords)}'."
    elif priority == "Urgent" and matched_severity_keywords:
        reason = f"Severity detected by: '{', '.join(matched_severity_keywords)}'."


    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str, schema: Dict[str, Any]):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    processed_rows = []
    original_headers = []

    try:
        with open(input_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            original_headers = reader.fieldnames if reader.fieldnames else []
            
            for i, row in enumerate(reader):
                # Initialize with default error state, to be overridden if successful
                classified_data = {
                    "complaint_id": row.get("complaint_id", "N/A"),
                    "category": "Error",
                    "priority": "Error",
                    "reason": "Processing Failed",
                    "flag": f"Processing Error - Line {i+2}" 
                }
                try:
                    # Pass the classification schema to classify_complaint
                    classified_data = classify_complaint(row, schema)
                    
                except Exception as e:
                    print(f"Error classifying row {i+2} (complaint_id: {row.get('complaint_id', 'N/A')}): {e}")
                    classified_data["flag"] = f"Runtime Error - Line {i+2}"
                    classified_data["reason"] = f"Failed to classify: {e}"
                
                # Combine original row data with classified data.
                output_row = {**row, **classified_data}
                processed_rows.append(output_row)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    # Determine all unique headers for the output file
    classification_headers = ["complaint_id", "category", "priority", "reason", "flag"]
    all_headers = list(original_headers)
    for h in classification_headers:
        if h not in all_headers:
            all_headers.append(h)

    # Write results to output CSV
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=all_headers)
            writer.writeheader()
            writer.writerows(processed_rows)
    except Exception as e:
        print(f"An error occurred while writing to the output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # Pass the defined CLASSIFICATION_SCHEMA to the batch_classify function
    batch_classify(args.input, args.output, CLASSIFICATION_SCHEMA)
    print(f"Done. Results written to {args.output}")

