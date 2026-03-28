"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from typing import Dict, Any

def classify_complaint(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # --- SIMULATED CLASSIFICATION LOGIC ---
    # This section is a placeholder. You would replace this with actual calls to your
    # AI tool or model based on your agents.md and skills.md.
    
    complaint_id = row.get("complaint_id", "N/A")
    # This line is crucial: It now correctly pulls text from the 'description' column
    # as per your sample input CSV.
    complaint_text = row.get("description", "").lower() 

    category = "Unknown"
    priority = "Low"
    reason = "Undetermined"
    flag = "Success"

    if not complaint_text:
        flag = "Null Data - Missing Description Text"
        category = "General"
        reason = "Missing Information"
        priority = "Medium"
    else:
        # Based on keywords observed in your provided sample data
        if "pothole" in complaint_text or "road surface cracked" in complaint_text or "manhole cover missing" in complaint_text:
            category = "Roads & Infrastructure"
            priority = "High"
            reason = "Road Hazard"
        elif "flooded" in complaint_text or "inaccessible" in complaint_text or "drain blocked" in complaint_text:
            category = "Drainage & Flooding"
            priority = "High"
            reason = "Flooding Issue"
        elif "streetlight" in complaint_text or "lights out" in complaint_text or "dark at night" in complaint_text:
            category = "Public Lighting"
            priority = "Medium"
            reason = "Lighting Malfunction"
        elif "garbage bins" in complaint_text or "bulk waste" in complaint_text:
            category = "Waste Management"
            priority = "Medium"
            reason = "Illegal Dumping/Overflow"
        elif "music past midnight" in complaint_text:
            category = "Public Nuisance"
            priority = "Low"
            reason = "Noise Complaint"
        elif "dead animal" in complaint_text:
            category = "Sanitation & Health"
            priority = "High"
            reason = "Health Hazard"
        elif "footpath tiles broken" in complaint_text:
            category = "Pedestrian Infrastructure"
            priority = "Medium"
            reason = "Footpath Hazard"
        else:
            category = "General Inquiry"
            priority = "Low"
            reason = "General Information"
            
    # Example RICE enforcement: If priority is High and it's a "Road Hazard" issue,
    # maybe add an extra flag or adjust reason. This is just a demonstration.
    # You would replace this with your actual RICE rules.
    if category == "Roads & Infrastructure" and priority == "High":
        reason = "Urgent Road Hazard - Safety Risk"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
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
                    "complaint_id": row.get("complaint_id", "N/A"), # Ensure complaint_id is always present
                    "category": "Error",
                    "priority": "Error",
                    "reason": "Processing Failed",
                    "flag": f"Processing Error - Line {i+2}" # Line i+2 because of header (assuming 1-based line numbering for error reporting)
                }
                try:
                    # Pass the full row to classify_complaint
                    classified_data = classify_complaint(row)
                    
                    # Additional check for critical fields in batch_classify if needed
                    # If classify_complaint already flagged it, don't override with a generic 'missing ID' flag
                    if not row.get("complaint_id") and classified_data["flag"] == "Success":
                        classified_data["flag"] = "Null Data - Missing Complaint ID"
                            
                except Exception as e:
                    # Catch any unexpected errors during classification of a single row
                    print(f"Error classifying row {i+2} (complaint_id: {row.get('complaint_id', 'N/A')}): {e}")
                    classified_data["flag"] = f"Runtime Error - Line {i+2}"
                    classified_data["reason"] = f"Failed to classify: {e}"
                
                # Combine original row data with classified data.
                # New classified data overwrites existing keys if they share names (e.g., 'flag').
                output_row = {**row, **classified_data}
                processed_rows.append(output_row)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    # Determine all unique headers for the output file
    # Ensure standard classification fields are always present and come last for consistency
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
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

