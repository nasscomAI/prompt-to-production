"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '')
    desc_lower = desc.lower()
    
    # Default values
    category = "Other"
    flag = ""
    
    # 1. Determine Category based on keywords
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "drain blocked" in desc_lower or "drain" in desc_lower:
        category = "Drain Blockage"
    elif "flood" in desc_lower:
        category = "Flooding"
    elif "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
    elif "music" in desc_lower or "noise" in desc_lower:
        category = "Noise"
    elif "crack" in desc_lower or "sinking" in desc_lower or "manhole" in desc_lower or "footpath" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower and "lights out" in desc_lower:
        # Ambiguous case: multiple conflicting keywords
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif "streetlight" in desc_lower or "lights out" in desc_lower or "dark" in desc_lower:
        category = "Streetlight"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
    else:
        # Unclear description
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # 2. Determine Priority based on severity keywords
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    triggered_keyword = ""
    for word in urgent_keywords:
        if word in desc_lower:
            priority = "Urgent"
            triggered_keyword = word
            break
            
    # 3. Formulate Reason citing specific words
    if flag == "NEEDS_REVIEW":
        reason = "The description contains ambiguous or conflicting information, setting flag to NEEDS_REVIEW."
    elif priority == "Urgent":
        reason = f"Classified as Urgent because the description mentions the severity keyword '{triggered_keyword}'."
    else:
        # Find a significant word from the description to cite
        words = [w for w in desc.split() if len(w) > 4]
        cited_word = words[0] if words else "various"
        reason = f"Classified as {category} based on the description mentioning '{cited_word}'."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("Input CSV has no header")
                
            # Set up new fieldnames
            new_fields = ["category", "priority", "reason", "flag"]
            out_fieldnames = fieldnames + [f for f in new_fields if f not in fieldnames]
            
            results = []
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Check for nulls/empty descriptions
                    if not row.get("description"):
                        row.update({
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Null or empty description provided.",
                            "flag": "NEEDS_REVIEW"
                        })
                    else:
                        classification = classify_complaint(row)
                        row.update(classification)
                    results.append(row)
                except Exception as e:
                    print(f"Error processing row {row_num} (ID: {row.get('complaint_id', 'Unknown')}): {e}")
                    row.update({
                        "category": "Error",
                        "priority": "Unknown",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "FAILED"
                    })
                    results.append(row)
                    
        if not results:
            print("No rows to process.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
    except Exception as e:
        print(f"Critical batch processing error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
