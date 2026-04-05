import argparse
import csv
import sys

def load_dataset(input_path, filter_ward, filter_category):
    """
    Reads the CSV, explicitly validates columns implicitly by unpacking rows, 
    and checks filtering boundaries.
    Crucially, computes the tally of missing values and reports them before returning.
    """
    # Enforcement 1: Never aggregate across wards or categories unless instructed
    if not filter_ward or filter_ward.lower() == "all":
        raise ValueError("REFUSAL: Agent is explicitly restricted from aggregating across all wards. Please specify an exact ward.")
    if not filter_category or filter_category.lower() == "all":
        raise ValueError("REFUSAL: Agent is explicitly restricted from aggregating across multiple categories.")

    data = []
    null_tallies = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Enforce single Ward + Category filtering context
            if row['ward'] == filter_ward and row['category'] == filter_category:
                actual_spend_raw = row['actual_spend'].strip()
                
                # Enforcement 2: Flag every null row explicitly before computing
                if not actual_spend_raw:
                    null_tallies.append(row)
                
                data.append(row)
                
    # Proactively log missing data and their reasons back to console to guarantee rules are surfaced
    print(f"[Dataset Review] Detected {len(null_tallies)} rows with a 'null' actual_spend for the isolated scope: {filter_ward} -> {filter_category}")
    for row in null_tallies:
        print(f"🚨 FLAG: Period {row['period']} is explicitly missing data. Notes specify: {row['notes']}")
        
    return data

def compute_growth(data, growth_type):
    """
    Evaluates growth rates per period securely, avoiding NaN compute crashes.
    Exposes its own formula linearly per row output.
    """
    # Enforcement 4: Guarantee growth_type is passed
    if not growth_type:
        raise ValueError("REFUSAL: Specific `--growth-type` is completely missing. Execution halted rather than guessing defaults.")
        
    if growth_type.upper() != "MOM":
        raise ValueError(f"REFUSAL: Unrecognized/Unsupported growth type '{growth_type}'. Only 'MoM' structured in this agent module.")

    data = sorted(data, key=lambda x: x['period'])
    results = []
    
    for i in range(len(data)):
        current = data[i]
        curr_spend_str = current['actual_spend'].strip()
        
        if not curr_spend_str:
            results.append({
                'Ward': current['ward'],
                'Category': current['category'],
                'Period': current['period'],
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': f"Must be flagged — not computed [{current['notes']}]"
            })
            continue
            
        curr_val = float(curr_spend_str)
        
        # Calculate MoM mathematically via (Curr - Prev) / Prev * 100
        if i == 0:
            growth_str = "n/a (first tracking period)"
        else:
            prev = data[i-1]
            prev_spend_str = prev['actual_spend'].strip()
            
            if not prev_spend_str:
                growth_str = "n/a (previous base period was NULL)"
            else:
                prev_val = float(prev_spend_str)
                if prev_val == 0:
                    growth_str = "n/a (divide by zero logic exception)"
                else:
                    growth_pct = ((curr_val - prev_val) / prev_val) * 100
                    sign = "+" if growth_pct > 0 else ""
                    
                    # Enforcement 3: Show the EXACT mathematical formula used on every output element
                    explicit_formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                    growth_str = f"{sign}{growth_pct:.1f}% [Formula: {explicit_formula}]"
                    
        results.append({
            'Ward': current['ward'],
            'Category': current['category'],
            'Period': current['period'],
            'Actual Spend (₹ lakh)': curr_val,
            'MoM Growth': growth_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Aggregator (Constrained)")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--ward", required=True, help="Specific Ward boundary")
    parser.add_argument("--category", required=True, help="Specific Category boundary")
    parser.add_argument("--growth-type", required=True, help="Mathematical metric (e.g., MoM)")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # Wrap argparse missing parameter closures to ensure prompt logic triggers fully
        print("REFUSAL: Missing restricted boundaries or command arguments, halting rather than silently guessing.")
        sys.exit(1)

    try:
        isolated_data = load_dataset(args.input, args.ward, args.category)
        table_results = compute_growth(isolated_data, args.growth_type)
        
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in table_results:
                writer.writerow(r)
                
        print(f"Processing Complete. Exported specific isolated metric view to {args.output}")
        
    except ValueError as ve:
        # Expected domain exceptions like REFUSAL logic
        print(str(ve))
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Critical Exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
