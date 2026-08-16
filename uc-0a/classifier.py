import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    # Combine all text in the row to search for keywords safely
    text = " ".join(str(v) for v in row.values()).lower()
    
    # Determine Category
    if any(word in text for word in ['road', 'pothole', 'street']):
        category = 'Roads'
    elif any(word in text for word in ['water', 'pipe', 'leak', 'drain']):
        category = 'Water Supply'
    elif any(word in text for word in ['garbage', 'waste', 'trash', 'sanitation']):
        category = 'Sanitation'
    else:
        category = 'Other'
        
    # Determine Priority
    if any(word in text for word in ['danger', 'leak', 'burst', 'urgent', 'injury']):
        priority = 'Urgent'
    else:
        priority = 'Normal'
        
    # Add tracking fields required by the RICE prompt
    flag = 'NEEDS_REVIEW' if category == 'Other' else 'OK'
    reason = 'Matched keywords' if category != 'Other' else 'No keywords matched'
    
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }

def batch_classify(input_path: str, output_path: str):
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            results = []
            
            for row in reader:
                # Skip completely empty rows
                if not row or all(not v for v in row.values()):
                    continue
                    
                try:
                    classification = classify_complaint(row)
                    # Merge the original row data with our new classification columns
                    merged_row = {**row, **classification}
                    results.append(merged_row)
                except Exception as e:
                    print(f"Skipping bad row: {e}")
                    
        if not results:
            print("No valid rows found.")
            return

        # Write the final data to the output file
        out_fieldnames = list(results[0].keys())
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")