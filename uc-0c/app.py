"""
UC-0C — Number That Looks Right
Implementation guided by agents.md and skills.md.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    rows = []
    null_rows_info = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing_cols = required_cols - fieldnames
        if missing_cols:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(missing_cols)}")
            
        for line_num, row in enumerate(reader, start=2): # Header is line 1
            # Clean up row keys and values
            cleaned_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
            
            # Check for null actual_spend
            actual_spend_str = cleaned_row.get('actual_spend', '')
            if actual_spend_str == '':
                null_rows_info.append(
                    f"Line {line_num}: period={cleaned_row['period']}, ward={cleaned_row['ward']}, "
                    f"category={cleaned_row['category']}, notes='{cleaned_row['notes']}'"
                )
            rows.append(cleaned_row)
            
    print(f"Dataset loaded. Total rows: {len(rows)}")
    print(f"Null actual_spend rows detected: {len(null_rows_info)}")
    for info in null_rows_info:
        print(f"  - {info}")
        
    return rows


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if not ward or ward.strip() == '' or ward.lower() == 'all':
        sys.exit("Error: Calculation across all wards is prohibited. Please specify a single ward.")
    if not category or category.strip() == '' or category.lower() == 'all':
        sys.exit("Error: Calculation across all categories is prohibited. Please specify a single category.")
    if not growth_type or growth_type.strip() == '':
        sys.exit("Error: Growth type must be specified. Please choose a growth type (e.g. MoM).")
    if growth_type.lower() != 'mom':
        sys.exit(f"Error: Growth type '{growth_type}' is not supported. Only 'MoM' is supported for this single-year dataset.")
        
    # Filter dataset for the selected ward and category
    filtered = [
        row for row in dataset
        if row['ward'].strip() == ward and row['category'].strip() == category
    ]
    
    if not filtered:
        print(f"Warning: No rows found matching ward='{ward}' and category='{category}'")
        return []
        
    # Sort chronological by period (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_spend_str = row['actual_spend']
        notes = row['notes']
        
        # Determine actual spend float or None
        actual_spend = None
        if actual_spend_str != '':
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                pass
                
        # Initialize output fields
        growth = "NULL"
        formula = "N/A"
        out_notes = notes
        
        if actual_spend is None:
            # Rule 3: Flag null row and report reason from notes column
            growth = "NULL"
            formula = "N/A"
            out_notes = notes if notes else "Actual spend is NULL"
        else:
            # We have a valid current spend. Check previous period for MoM
            if i == 0:
                growth = "NULL"
                formula = "N/A"
                out_notes = "First period in dataset (no prior data)"
            else:
                prev_row = filtered[i-1]
                prev_spend_str = prev_row['actual_spend']
                prev_spend = None
                if prev_spend_str != '':
                    try:
                        prev_spend = float(prev_spend_str)
                    except ValueError:
                        pass
                        
                if prev_spend is None:
                    # Rule 4: If previous period spend is null
                    growth = "NULL"
                    formula = "N/A"
                    out_notes = f"Prior period spend is NULL (reason: {prev_row['notes']})"
                else:
                    # Both current and previous are valid floats. Compute growth!
                    if prev_spend == 0:
                        growth = "NULL"
                        formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                        out_notes = "Cannot divide by zero (prior spend is 0)"
                    else:
                        val = ((actual_spend - prev_spend) / prev_spend) * 100
                        # Format signed MoM growth
                        growth = f"{'+' if val >= 0 else ''}{val:.1f}%"
                        formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                        
        output_rows.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_spend_str if actual_spend_str != '' else 'NULL',
            'growth': growth,
            'formula': formula,
            'notes': out_notes
        })
        
    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C — Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    # Make arguments optional in argparse, but enforce them in code to return friendly refusal messages
    parser.add_argument("--ward", required=False, help="Ward name to filter by")
    parser.add_argument("--category", required=False, help="Category name to filter by")
    parser.add_argument("--growth-type", required=False, help="Growth type calculation (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    # Enforce required fields manually to handle "refuse and ask, never guess"
    if not args.ward:
        sys.exit("Refusal: --ward is not specified. Please specify a single ward to analyze.")
    if not args.category:
        sys.exit("Refusal: --category is not specified. Please specify a single category to analyze.")
    if not args.growth_type:
        sys.exit("Refusal: --growth-type is not specified. Please specify the growth type (e.g. MoM).")

    try:
        dataset = load_dataset(args.input)
        output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if not output_rows:
            print("No output generated.")
            sys.exit(0)
            
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Write output table
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
            
        print(f"Done. Growth calculation output written to {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e


if __name__ == "__main__":
    main()
