"""
UC-0C app.py — Number That Looks Right.
Data analysis agent to compute per-ward and per-category growth metrics (MoM).
"""
import sys
import os
import csv
import argparse

def refuse(message):
    """Prints a strict refusal message and exits with code 1."""
    print(f"REFUSAL: {message}", file=sys.stderr)
    sys.exit(1)

def load_dataset(input_path):
    """
    Reads the CSV dataset from the specified path.
    Validates required schema columns, reports the count and details
    of null actual_spend rows, and returns the dataset.
    """
    print(f"Reading dataset from {input_path}...")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset file not found at {input_path}")
    
    rows = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Schema validation
        expected_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        for col in expected_columns:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column in CSV schema: {col}")
        
        for line_num, row in enumerate(reader, start=2):
            # Parse budgeted_amount
            try:
                row['budgeted_amount'] = float(row['budgeted_amount'])
            except ValueError:
                raise ValueError(f"Row {line_num}: invalid budgeted_amount '{row['budgeted_amount']}'")
            
            # Parse actual_spend
            actual_spend_str = row['actual_spend'].strip()
            if actual_spend_str == "":
                row['actual_spend'] = None
                null_rows.append(row)
            else:
                try:
                    row['actual_spend'] = float(actual_spend_str)
                except ValueError:
                    raise ValueError(f"Row {line_num}: invalid actual_spend '{row['actual_spend']}'")
            
            rows.append(row)
            
    print(f"Successfully loaded {len(rows)} rows.")
    print(f"Found {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Period: {nr['period']}, Ward: {nr['ward']}, Category: {nr['category']} (Reason: {nr['notes']})")
        
    return rows

def compute_growth(dataset, ward, category, growth_type):
    """
    Computes period-over-period growth metrics for a single ward + category.
    Handles null values, shows the exact calculation formulas,
    and flags missing baselines.
    """
    # Boundary validation: No aggregations allowed
    unique_wards = set(r['ward'] for r in dataset)
    unique_categories = set(r['category'] for r in dataset)
    
    if ward not in unique_wards:
        refuse(f"Ward '{ward}' not found in dataset. Available wards: {sorted(list(unique_wards))}")
        
    if category not in unique_categories:
        refuse(f"Category '{category}' not found in dataset. Available categories: {sorted(list(unique_categories))}")
        
    # Filter and sort chronologically
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda r: r['period'])
    
    output_rows = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        current_spend = row['actual_spend']
        budgeted_amount = row['budgeted_amount']
        notes = row['notes']
        
        # Default empty/null placeholders
        growth_pct_str = "NULL"
        formula_str = "N/A"
        
        if current_spend is None:
            # Rule 2: Flag every null row before computing, report null reason
            growth_pct_str = "NULL"
            formula_str = "N/A"
            if not notes:
                notes = "Actual spend is null (no reason provided)"
        elif i == 0:
            # Baseline period (no prior month exists in the 2024 timeline)
            growth_pct_str = "NULL"
            formula_str = "N/A"
            if not notes:
                notes = "Initial period, no baseline"
        else:
            prev_row = filtered[i - 1]
            prev_spend = prev_row['actual_spend']
            
            if prev_spend is None:
                growth_pct_str = "NULL"
                formula_str = "N/A"
                # Handle subsequent month of a null baseline gracefully
                null_reason = prev_row['notes'] if prev_row['notes'] else "missing data"
                notes = f"Cannot compute MoM: Previous month ({prev_row['period']}) spend is NULL ({null_reason})"
            else:
                # Normal MoM computation
                diff = current_spend - prev_spend
                pct = (diff / prev_spend) * 100
                
                # Rule 3: Show formula used in every output row alongside the result
                formula_str = f"({current_spend} - {prev_spend}) / {prev_spend}"
                
                # Format growth percentage with sign and one decimal place
                if pct > 0:
                    growth_pct_str = f"+{pct:.1f}%"
                elif pct < 0:
                    growth_pct_str = f"-{abs(pct):.1f}%"
                else:
                    growth_pct_str = "0.0%"
                    
        # Append calculated row
        out_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': budgeted_amount,
            'actual_spend': "NULL" if current_spend is None else current_spend,
            'growth_percentage': growth_pct_str,
            'formula': formula_str,
            'notes': notes
        }
        output_rows.append(out_row)
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C — Number That Looks Right (Growth Metric Calculator)")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to input budget CSV file")
    parser.add_argument("--ward", help="Target ward (no aggregations allowed)")
    parser.add_argument("--category", help="Target category (no aggregations allowed)")
    parser.add_argument("--growth-type", help="Growth type to calculate (e.g. MoM)")
    parser.add_argument("--output", default="growth_output.csv", help="Path to save output CSV file")
    
    args = parser.parse_args()
    
    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        refuse("Growth type is not specified. Please specify --growth-type (e.g., MoM).")
        
    if args.growth_type.upper() != "MOM":
        refuse(f"Unsupported growth-type '{args.growth_type}'. Only 'MoM' is supported.")
        
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or args.ward.strip().lower() in ["all", "any", "aggregated", "*"]:
        refuse("Ward must be explicitly specified. Aggregated queries or multi-ward requests are not allowed.")
        
    if not args.category or args.category.strip().lower() in ["all", "any", "aggregated", "*"]:
        refuse("Category must be explicitly specified. Aggregated queries or multi-category requests are not allowed.")
        
    # Load dataset
    try:
        dataset = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Compute growth
    output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    # Save output to CSV
    fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_percentage', 'formula', 'notes']
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in output_rows:
                writer.writerow(row)
        print(f"Success! Per-ward per-category growth output written to {args.output}")
    except Exception as e:
        print(f"Error writing output CSV: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
