"""
UC-0C — Number That Looks Right
Starter file. Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Read CSV, validate columns, and return the rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")
        
    rows = []
    null_rows_info = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames)):
            print(f"Error: Missing required columns in input CSV. Got: {reader.fieldnames}")
            sys.exit(1)
            
        for line_no, row in enumerate(reader, start=2):
            # Parse budgeted_amount safely
            try:
                row['budgeted_amount'] = float(row['budgeted_amount']) if row.get('budgeted_amount') else 0.0
            except ValueError:
                row['budgeted_amount'] = 0.0
                
            # Parse actual_spend safely
            actual_str = row.get('actual_spend', '').strip()
            if actual_str == '':
                row['actual_spend'] = None
                null_rows_info.append((line_no, row.get('period'), row.get('ward'), row.get('category'), row.get('notes')))
            else:
                try:
                    row['actual_spend'] = float(actual_str)
                except ValueError:
                    row['actual_spend'] = None
                    null_rows_info.append((line_no, row.get('period'), row.get('ward'), row.get('category'), row.get('notes')))
            
            rows.append(row)
            
    print(f"Loaded {len(rows)} rows from dataset.")
    print(f"Found {len(null_rows_info)} rows with NULL actual spend:")
    for info in null_rows_info:
        print(f"  Line {info[0]} | Period: {info[1]} | Ward: {info[2]} | Category: {info[3]} | Reason: {info[4]}")
        
    return rows


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter data by ward and category, sort by period, and compute MoM or YoY growth.
    """
    # Filter rows matching ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda r: r['period'])
    
    output_rows = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend']
        budget = row['budgeted_amount']
        notes = row.get('notes', '').strip()
        
        growth_rate = ""
        formula = "n/a"
        status_notes = ""
        
        if actual is None:
            status_notes = f"NULL value: {notes}" if notes else "NULL value."
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": "",
                "growth_rate": growth_rate,
                "formula": formula,
                "status_notes": status_notes
            })
            continue
            
        prev_row = None
        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i - 1]
            else:
                status_notes = "First period in dataset (no previous month)."
        elif growth_type == "YoY":
            # Find the row from 12 months ago
            curr_parts = period.split('-')
            if len(curr_parts) == 2:
                curr_yr, curr_mo = int(curr_parts[0]), int(curr_parts[1])
                target_yr = curr_yr - 1
                target_period = f"{target_yr:04d}-{curr_mo:02d}"
                for r in filtered:
                    if r['period'] == target_period:
                        prev_row = r
                        break
                if not prev_row:
                    status_notes = f"No data found for previous year's month: {target_period}."
        
        if prev_row:
            prev_actual = prev_row['actual_spend']
            prev_period = prev_row['period']
            prev_notes = prev_row.get('notes', '').strip()
            
            if prev_actual is None:
                status_notes = f"Cannot calculate growth: previous period ({prev_period}) actual spend was NULL ({prev_notes})."
            elif prev_actual == 0.0:
                status_notes = f"Cannot calculate growth: previous period ({prev_period}) actual spend was 0.0."
            else:
                # Calculate growth rate
                val = ((actual - prev_actual) / prev_actual) * 100
                if val > 0:
                    growth_rate = f"+{val:.1f}%"
                elif val < 0:
                    growth_rate = f"{val:.1f}%"
                else:
                    growth_rate = "0.0%"
                
                # Format math formula
                formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
                status_notes = f"Computed {growth_type} growth."
        elif not status_notes:
            status_notes = f"No previous reference period found for {growth_type}."
            
        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budget,
            "actual_spend": actual,
            "growth_rate": growth_rate,
            "formula": formula,
            "status_notes": status_notes
        })
        
    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze (refuses broad aggregation if missing)")
    parser.add_argument("--category", required=False, help="Specific category to analyze (refuses broad aggregation if missing)")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output growth CSV")
    
    args = parser.parse_args()
    
    # Enforce Rule 1: Never aggregate across wards or categories.
    if not args.ward or not args.category:
        print("Error: Refusing computation. Aggregating across multiple wards or categories is strictly prohibited. You must specify a single --ward and a single --category.")
        sys.exit(1)
        
    # Enforce Rule 2: Growth-type must be specified explicitly.
    if not args.growth_type:
        print("Error: Refusing computation. Growth type not specified. Please specify --growth-type (MoM or YoY) explicitly.")
        sys.exit(1)
        
    if args.growth_type not in ("MoM", "YoY"):
        print(f"Error: Refusing computation. Invalid growth type '{args.growth_type}' specified. Must be MoM or YoY.")
        sys.exit(1)
        
    print(f"Analyzing Budget Growth:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    print(f"  Growth Type: {args.growth_type}")
    
    # Load dataset
    data = load_dataset(args.input)
    
    # Compute growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Write output CSV
    fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_rate', 'formula', 'status_notes']
    with open(args.output, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth analysis written to {args.output}")

if __name__ == "__main__":
    main()
