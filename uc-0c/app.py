"""
UC-0C app.py — Budget Growth Calculator
Implemented using rules derived from README.md, agents.md, and skills.md.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads the CSV dataset, validates columns, and explicitly reports
    any null counts and their reasons before returning.
    """
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers or not all(col in headers for col in required_cols):
                print(f"Error: Missing required columns in input. Found: {headers}")
                sys.exit(1)
                
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: File not found at {input_path}")
        sys.exit(1)
        
    # Validation step: Explicitly flag nulls
    null_rows = [row for row in data if not row['actual_spend'].strip()]
    
    if null_rows:
        print("--- Null Value Report ---")
        print(f"Found {len(null_rows)} rows explicitly missing actual_spend:")
        for r in null_rows:
            print(f" - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
        print("-------------------------\n")
        
    return data

def compute_growth(data: list, target_ward: str, target_category: str, growth_type: str) -> list:
    """
    Computes per-period growth. Strictly forbids cross-ward/cross-category aggregation.
    Displays formulas and handles nulls gracefully without silent calculation dropping.
    """
    if target_ward.lower() == 'all' or target_category.lower() == 'all':
        print("Error: Aggregation across wards or categories is strictly forbidden by policy. Run individually.")
        sys.exit(1)
        
    if growth_type not in ['MoM', 'YoY']:
        print(f"Error: Unrecognized growth_type '{growth_type}'. Expecting 'MoM' or 'YoY'.")
        sys.exit(1)
        
    filtered = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]
    
    if not filtered:
        print(f"Error: No matching data found for Ward: '{target_ward}' and Category: '{target_category}'")
        sys.exit(1)
        
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        output_row = {
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual if actual else 'NULL',
            'MoM Growth': '',
            'Formula': ''
        }
        
        if not actual:
            output_row['MoM Growth'] = f"FLAGGED: NULL VALUE"
            output_row['Formula'] = f"Cannot compute: {notes}"
        elif i == 0 or (growth_type == 'YoY' and i < 12):
            output_row['MoM Growth'] = "n/a"
            output_row['Formula'] = "n/a (baseline period)"
        else:
            prev_row = filtered[i - 1] if growth_type == 'MoM' else filtered[i - 12]
            prev_actual = prev_row['actual_spend'].strip()
            
            if not prev_actual:
                output_row['MoM Growth'] = "FLAGGED: PREV PERIOD NULL"
                output_row['Formula'] = f"Cannot compute: previous period ({prev_row['period']}) missing"
            else:
                curr_val = float(actual)
                prev_val = float(prev_actual)
                growth = ((curr_val - prev_val) / prev_val) * 100
                sign = "+" if growth > 0 else ""
                output_row['MoM Growth'] = f"{sign}{growth:.1f}%"
                output_row['Formula'] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                
        results.append(output_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to csv dataset")
    parser.add_argument("--ward", required=False, help="Target ward to compute")
    parser.add_argument("--category", required=False, help="Target category to compute")
    parser.add_argument("--growth-type", required=False, help="Calculation method (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output csv")
    
    args = parser.parse_args()
    
    # Enforcement checks
    if not args.growth_type:
        print("Error: --growth-type parameter missing! Refusing to guess calculation method.")
        sys.exit(1)
    if not args.ward or not args.category:
        print("Error: Must specify explicitly both --ward and --category to avoid accidental aggregation.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth', 'Formula']
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Done. Output successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
