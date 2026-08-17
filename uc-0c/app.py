import csv
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Extract budget data without aggregation.')
    parser.add_argument('--input', required=True, help='Path to input CSV')
    parser.add_argument('--output', required=True, help='Path to output CSV')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Could not find input file at {args.input}")
        return

    # Read the raw data
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Write the strictly extracted data (forcing per-ward, per-category only, NO math)
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            
    print(f"✅ Success! Extracted data without aggregation and saved to {args.output}")

if __name__ == '__main__':
    main()