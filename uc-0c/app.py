import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Skill: load_dataset
    Reads the CSV data, validates columns, and explicitly reports the count and exact rows of null values before returning the dataset.
    """
    dataset = []
    null_report = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate required columns
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError(f"CSV is missing required columns. Expected: {required_cols}")
                
            for row in reader:
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_report.append(f"Row {reader.line_num}: {row['period']} - {row['ward']} - {row['category']} -> Null Reason: {row['notes']}")

    except FileNotFoundError:
        print(f"Error: Could not find file at {filepath}")
        sys.exit(1)
        
    print(f"--- Data Loading Report ---")
    print(f"Total rows loaded: {len(dataset)}")
    print(f"Total null 'actual_spend' values found: {len(null_report)}")
    for report in null_report:
        print(f"  - {report}")
    print(f"---------------------------\n")
    
    return dataset

def compute_growth(dataset, target_ward, target_category, growth_type):
    """
    Skill: compute_growth
    Computes requested growth metric for a specific ward and category, returning a per-period table with explicit formula tracking.
    """
    if not growth_type:
        print("Refusal: --growth-type is not specified. I will not guess. Please specify it (e.g. MoM).")
        sys.exit(1)
        
    if not target_ward or not target_category:
        print("Refusal: Never aggregate across wards or categories unless explicitly instructed. Please provide both target ward and category.")
        sys.exit(1)
        
    filtered = [row for row in dataset if row['ward'] == target_ward and row['category'] == target_category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        spend_str = row['actual_spend'].strip()
        notes = row['notes']
        
        if not spend_str:
            results.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': f'FLAGGED: {notes}',
                'Formula': 'n/a (Null spend)'
            })
            prev_spend = None
            continue
            
        current_spend = float(spend_str)
        if prev_spend is None:
            results.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend (₹ lakh)': f"{current_spend}",
                'MoM Growth': 'n/a',
                'Formula': 'n/a (No previous valid period)'
            })
        else:
            growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
            sign = "+" if growth_pct > 0 else ""
            formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            results.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend (₹ lakh)': f"{current_spend}",
                'MoM Growth': f"{sign}{growth_pct:.1f}%",
                'Formula': formula
            })
            
        prev_spend = current_spend

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analyst Agent")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", default=None, help="Specific ward to analyze")
    parser.add_argument("--category", default=None, help="Specific category to analyze")
    parser.add_argument("--growth-type", default=None, help="Type of growth to compute (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # rule 1 & rule 4 enforcements prior to proceeding
    if not args.ward or not args.category:
        print("Refusal: Never aggregate across wards or categories unless explicitly instructed. Request refused.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Refusal: --growth-type is not specified. I will not guess. Request refused.")
        sys.exit(1)

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if results:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth', 'Formula'])
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Done. Per-ward per-category summary table generated successfully at {args.output}")
    else:
        print("No matching data found for the given ward and category.")

if __name__ == "__main__":
    main()
