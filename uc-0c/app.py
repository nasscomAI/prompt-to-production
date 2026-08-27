import argparse
import csv
import sys

def load_dataset(filepath: str):
    """
    Reads the CSV, validates columns, and explicitly flags deliberate null rows.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames if reader.fieldnames else [])
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Dataset '{filepath}' not found.")
        sys.exit(1)
        
    expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not expected_cols.issubset(fieldnames):
        print(f"ERROR: Missing required columns in dataset. Expected {expected_cols}.")
        sys.exit(1)
        
    # Flag deliberate null actual_spend values
    null_count = 0
    null_reports = []
    
    for row in rows:
        if not row['actual_spend'].strip():
            null_count += 1
            null_reports.append(f"Period: {row['period']} | Ward: {row['ward']} | Category: {row['category']} | Reason: {row['notes']}")
            
    if null_count > 0:
        print(f"WARNING: Detected {null_count} rows with deliberate null 'actual_spend' values.")
        for report in null_reports:
            print(f"  - {report}")
            
    return rows

def compute_growth(rows, ward, category, growth_type):
    """
    Computes per-period growth for a specific ward and category.
    Shows the exact formula and strictly handles nulls.
    """
    if ward.lower() == 'any' or category.lower() == 'any':
        print("ERROR: Operation attempts to aggregate data across multiple wards or categories. Request REFUSED.")
        sys.exit(1)
        
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        print(f"WARNING: No data found for Ward '{ward}' and Category '{category}'.")
        return []
        
    # Sort strictly by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        
        if not actual_str:
            actual_val_display = "NULL"
            reason = row['notes']
            metric_val = f"Must be flagged — not computed. Reason: {reason}"
        else:
            actual_val_display = actual_str
            actual_spend = float(actual_str)
            
            if growth_type.upper() == 'MOM':
                if i == 0:
                    metric_val = "n/a [Formula: No previous month data]"
                else:
                    prev_str = filtered[i-1]['actual_spend'].strip()
                    if not prev_str:
                        metric_val = "n/a [Formula: Previous month was NULL]"
                    else:
                        prev_spend = float(prev_str)
                        if prev_spend == 0:
                            metric_val = "n/a [Formula: Division by zero]"
                        else:
                            growth = (actual_spend - prev_spend) / prev_spend
                            sign = "+" if growth > 0 else ""
                            metric_val = f"{sign}{growth*100:.1f}% [Formula: ({actual_spend} - {prev_spend}) / {prev_spend}]"
            elif growth_type.upper() == 'YOY':
                metric_val = "n/a [Formula: Insufficient multi-year data for YoY]"
            else:
                print(f"ERROR: Unknown growth type '{growth_type}'.")
                sys.exit(1)
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual_val_display,
            f'{growth_type} Growth': metric_val
        })
        
    return results

def main():
    # Use argparse without required on --growth-type to explicitly handle omission
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analyst")
    parser.add_argument("--input", required=True, help="Path to input dataset CSV")
    parser.add_argument("--ward", required=True, help="Target ward")
    parser.add_argument("--category", required=True, help="Target category")
    parser.add_argument("--growth-type", required=False, help="Growth type metric (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    # Enforcement Rule 4: If --growth-type not specified, refuse and ask
    if not args.growth_type:
        print("ERROR: --growth-type was not specified. Refusing to guess the formula.")
        print("Please rerun the command with an explicit --growth-type (e.g., --growth-type MoM).")
        sys.exit(1)

    print("Loading dataset...")
    rows = load_dataset(args.input)
    
    print(f"Computing {args.growth_type} growth for '{args.ward}' - '{args.category}'...")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    if results:
        fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth']
        try:
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Output written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
