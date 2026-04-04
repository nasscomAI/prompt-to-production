import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Skill: Reads CSV dataset, validates columns, and reports on completeness before processing.
    """
    dataset = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing required columns. Expected: {required_cols}")
                
            null_count = 0
            null_rows = []
            
            for row in reader:
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_count += 1
                    null_rows.append(f"{row['period']} | {row['ward']} | {row['category']} -> Reason: {row['notes']}")
                    
            print(f"Validation Report: Found {null_count} null 'actual_spend' values.")
            for nr in null_rows:
                print(f"  - {nr}")
                
        return dataset
        
    except FileNotFoundError:
        raise ValueError(f"Dataset not found at {filepath}")

def compute_growth(dataset, target_ward, target_category, growth_type):
    """
    Skill: Calculates growth metrics for a strictly specified ward and category based on growth_type.
    """
    # Enforcement 1: Never aggregate across wards or categories unless explicitly instructed
    if target_ward.lower() == 'all' or target_category.lower() == 'all':
        raise ValueError("Enforcement 1: Refusing to aggregate across 'All' wards or categories.")
    
    # Enforcement 4: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        raise ValueError("Enforcement 4: --growth-type not specified. Refuting to guess default (e.g., MoM/YoY). Please specify.")
    
    if growth_type.lower() != 'mom':
        raise ValueError(f"Unsupported growth_type: {growth_type}. Only 'MoM' is supported currently.")
        
    filtered_data = [row for row in dataset if row['ward'] == target_ward and row['category'] == target_category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: {target_ward}, Category: {target_category}")
        return []
        
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered_data:
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        # Enforcement 2: Flag every null row before computing and report null reason
        if not actual_spend_str:
            results.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': 'NULL',
                'Formula / Notes': f"FLAGGED NULL: {notes}"
            })
            prev_spend = None # Cannot calculate next month's growth relative to a null month
            continue
            
        current_spend = float(actual_spend_str)
        
        if prev_spend is None:
            growth_pct = 'N/A'
            formula_used = 'N/A (No prior reference month)'
        else:
            if prev_spend == 0:
                growth_pct = 'N/A'
                formula_used = 'Cannot divide by zero'
            else:
                growth = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth > 0 else "−" if growth < 0 else ""
                growth_pct = f"{sign}{abs(growth):.1f}%"
                
                # Enforcement 3: Show formula used in every output row alongside the result
                formula_used = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                
        results.append({
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend (₹ lakh)': current_spend,
            'MoM Growth': growth_pct,
            'Formula / Notes': formula_used
        })
        
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Agent")
    parser.add_argument("--input", required=True, help="Path to input CSV dataset")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze (No 'All')")
    parser.add_argument("--category", required=True, help="Specific category to analyze (No 'All')")
    parser.add_argument("--growth-type", required=False, help="Calculation type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    try:
        # Step 1: Execute load_dataset skill
        dataset = load_dataset(args.input)
        
        # Step 2: Execute compute_growth skill
        growth_results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        # Step 3: Write verifiable output
        if growth_results:
            fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth', 'Formula / Notes']
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(growth_results)
                
            print(f"\nSuccess: Exported {len(growth_results)} rows to {args.output}")
        else:
            print("\nWarning: No rows to output based on the filtering criteria.")
            
    except Exception as e:
        print(f"Agent Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
