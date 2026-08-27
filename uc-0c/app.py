import argparse
import csv
import sys
import os
from datetime import datetime

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the budget CSV, validates essential columns, and identifies all null rows with their associated notes.
    """
    if not os.path.exists(file_path):
        print(f"Refusal: Input file not found at {file_path}")
        sys.exit(1)
    
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mandatory_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            
            # Check headers
            headers = reader.fieldnames
            if headers is None or not all(col in headers for col in mandatory_columns):
                missing = [col for col in mandatory_columns if headers is None or col not in headers]
                print(f"Refusal: Dataset is missing required columns: {missing}")
                sys.exit(1)
            
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Refusal: Failed to read CSV. Error: {e}")
        sys.exit(1)

    # Enforcement Rule 2: Flag null rows immediately
    null_rows = [r for r in data if not r['actual_spend'] or r['actual_spend'].strip() == ""]
    if null_rows:
        print(f"FYI: Identified {len(null_rows)} null rows in dataset:")
        for r in null_rows:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates growth (MoM/YoY) for a filtered subset (ward + category) and generates a detailed report with formulas.
    """
    # Filter for the specific ward and category
    subset = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not subset:
        print(f"Refusal: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    # Enrollment Rule 1: No unauthorized aggregation.
    # We already filtered by single ward/cat, so we are safe. 
    # If a user requested "all" via some pattern, subset would have them, but our CLI requires explicit values.
    
    # Sort chronologically (period is YYYY-MM)
    subset.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(subset):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes']
        
        entry = {
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual_str if actual_str else "NULL",
            'growth': "",
            'formula': ""
        }
        
        # Enforcement Rule 2: Flag null rows
        if not actual_str:
            entry['growth'] = "FLAGGED"
            entry['formula'] = f"Not computed | Reason: {notes}"
            results.append(entry)
            continue
            
        actual = float(actual_str)
        prev_row = None
        
        if growth_type == 'MoM':
            if i > 0:
                prev_row = subset[i-1]
        elif growth_type == 'YoY':
            # Find period exactly 1 year ago
            try:
                curr_y, curr_m = map(int, period.split('-'))
                prev_y = curr_y - 1
                target_period = f"{prev_y:04d}-{curr_m:02d}"
                prev_matches = [r for r in subset if r['period'] == target_period]
                if prev_matches:
                    prev_row = prev_matches[0]
            except:
                pass
        
        if prev_row:
            prev_actual_str = prev_row['actual_spend'].strip()
            if not prev_actual_str:
                entry['growth'] = "N/A"
                entry['formula'] = f"Cannot compute | Prior period spend was NULL ({prev_row['notes']})"
            else:
                prev_actual = float(prev_actual_str)
                # Enforcement Rule 3: Show formula
                growth_val = ((actual - prev_actual) / prev_actual) * 100
                prefix = "+" if growth_val >= 0 else ""
                entry['growth'] = f"{prefix}{growth_val:.1f}%"
                entry['formula'] = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
        else:
            entry['growth'] = "N/A"
            entry['formula'] = "First available period"
            
        results.append(entry)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", help="Must be MoM or YoY")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Enforcement Rule 4: Refuse if --growth-type is not specified
    if not args.growth_type:
        print("Refusal: --growth-type is mandatory. Please specify MoM or YoY. I cannot guess the intended calculation.")
        sys.exit(1)

    if args.growth_type not in ['MoM', 'YoY']:
        print(f"Refusal: Unknown growth type '{args.growth_type}'. Use MoM or YoY.")
        sys.exit(1)

    # Process
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save output
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth', 'formula'])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nSuccess. Growth table saved to {args.output}")
        print("\nVerification Snip:")
        print(f"{'Period':<10} | {'Spend':<8} | {'Growth':<10} | {'Formula'}")
        print("-" * 60)
        for i in range(min(12, len(results))):
            r = results[i]
            print(f"{r['period']:<10} | {r['actual_spend']:<8} | {r['growth']:<10} | {r['formula']}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
