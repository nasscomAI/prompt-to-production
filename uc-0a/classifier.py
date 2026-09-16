import argparse
import csv
import sys

def batch_classify(input_file, output_file):
    # Define keywords that trigger high/critical severity escalation
    escalation_keywords = ["injury", "injured", "child", "children", "school", "hospital", "live wire", "hazard"]

    try:
        with open(input_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            # Ensure output file includes classification columns if not already present
            if fieldnames and 'category' not in fieldnames:
                fieldnames = list(fieldnames) + ['category', 'severity']
            
            rows = []
            for row in reader:
                description = row.get('description', '').lower()
                
                # Determine category (default fallback)
                category = row.get('category', 'General')
                
                # Determine severity based on rules/keywords
                severity = row.get('severity', 'Medium')
                for keyword in escalation_keywords:
                    if keyword in description:
                        severity = 'High'
                        break
                
                row['category'] = category
                row['severity'] = severity
                rows.append(row)

        # Write output file
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"Successfully processed {input_file} and saved results to {output_file}")

    except Exception as e:
        print(f"Error processing files: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Civic Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)