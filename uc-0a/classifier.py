import argparse
import csv
import os
import glob
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules from agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = str(row.get("description", "")).lower()
    
    # Check severity keywords for priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        # Match word boundaries to prevent substring matches (e.g. 'child' in 'childhood' is okay mostly, but let's be safe)
        if re.search(r'\b' + re.escape(kw) + r'\b', description):
            priority = "Urgent"
            break
            
    # Define category keywords mappings
    category_map = {
        "Pothole": ["pothole", "potholes", "crater"],
        "Flooding": ["flood", "flooding", "flooded", "waterlog", "waterlogged", "water"],
        "Streetlight": ["streetlight", "streetlights", "light", "dark", "unlit", "bulb"],
        "Waste": ["waste", "garbage", "trash", "rubbish", "dump"],
        "Noise": ["noise", "loud", "sound", "music"],
        "Road Damage": ["road damage", "crack", "cracked", "broken road"],
        "Heritage Damage": ["heritage", "monument", "statue", "old building"],
        "Heat Hazard": ["heat", "hot", "stroke", "wave", "heatwave"],
        "Drain Blockage": ["drain", "block", "blocked", "clog", "sewer"]
    }
    
    matched_categories = set()
    cited_words = []
    
    if not description.strip():
        # Handle completely empty/null description
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "The description provided is null or completely empty."
    else:
        for cat, keywords in category_map.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', description):
                    matched_categories.add(cat)
                    cited_words.append(kw)
                    
        matched_list = list(matched_categories)
        if not matched_list:
            category = "Other"
            flag = "NEEDS_REVIEW"
            reason = "The complaint does not contain specific keywords mapping to allowed categories."
        elif len(matched_list) == 1:
            category = matched_list[0]
            flag = ""
            reason = f"The classification is based on explicitly citing the word '{cited_words[0]}' from the description."
        else:
            category = matched_list[0]
            flag = "NEEDS_REVIEW"
            reason = f"The complaint is ambiguous, citing conflicting words like '{cited_words[0]}' and '{cited_words[1]}'."

    return {
        "complaint_id": row.get("complaint_id", row.get("id", "")),
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
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for i, row in enumerate(reader, start=1):
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Gracefully handle any unexpected errors during row processing
                    print(f"Error processing row {i}: {e}")
                    results.append({
                        "complaint_id": str(i),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error occurred during classification: {str(e)}.",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Fatal error reading input file {input_path}: {e}")
        return

    # Check that we processed something
    if not results:
        print("No valid rows were processed. Results not written.")
        return

    # Write out the results
    try:
        # Standard fieldnames for output
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Fatal error writing output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=False, help="Path to a single test_[city].csv")
    parser.add_argument("--output", required=False, help="Path to write a single results CSV")
    parser.add_argument("--input_dir", default="../data/city-test-files", help="Directory containing test_[city].csv")
    parser.add_argument("--output_dir", default=".", help="Directory to save results_[city].csv")
    args = parser.parse_args()
    
    if args.input and args.output:
        # Fallback to single file processing
        batch_classify(args.input, args.output)
        print(f"Done. Single file results written to {args.output}")
    else:
        # Default batch processing mode
        search_path = os.path.join(args.input_dir, "test_*.csv")
        input_files = glob.glob(search_path)
        
        if not input_files:
            print(f"No test files found in {search_path}")
        else:
            for file_path in input_files:
                file_name = os.path.basename(file_path)
                output_name = file_name.replace("test_", "results_")
                output_path = os.path.join(args.output_dir, output_name)
                
                print(f"Processing {file_name} -> {output_name}...")
                batch_classify(file_path, output_path)
                
            print(f"Done. All results written to {args.output_dir}")
