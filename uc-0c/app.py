"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(file_path: str, target_ward: str, target_category: str) -> list:
    """Reads CSV, validates, reports nulls, and filters data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Could not find dataset at {file_path}")

    # Validate columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_cols.issubset(set(reader.fieldnames)):
        raise ValueError(f"Missing required columns. Expected {required_cols}")

    filtered_data = []
    null_reports = []

    for row in data:
        if row['ward'] == target_ward and row['category'] == target_category:
            actual_spend_str = row['actual_spend'].strip()
            
            # Check for nulls explicitly
            if not actual_spend_str:
                null_reports.append(f"Period {row['period']}: Null actual_spend. Reason: {row['notes']}")
                row['actual_spend'] = None
            else:
                try:
                    row['actual_spend'] = float(actual_spend_str)
                except ValueError:
                    row['actual_spend'] = None
                    null_reports.append(f"Period {row['period']}: Invalid actual_spend '{actual_spend_str}'. Reason: {row['notes']}")
            
            filtered_data.append(row)

    if null_reports:
        print("\n--- NULL VALUES DETECTED ---")
        for report in null_reports:
            print(report)
        print("----------------------------\n")

    return filtered_data

def compute_growth(data: list, growth_type: str) -> list:
    """Calculates MoM or YoY growth for actual_spend, returning formatted results with formula."""
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified. Cannot compute growth without explicit instruction.")
    
    if growth_type.lower() not in ['mom', 'yoy']:
        raise ValueError(f"REFUSAL: Unknown growth type '{growth_type}'. Only 'MoM' or 'YoY' supported.")

    # Sort data by period chronologically
    data.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(data)):
        current_row = data[i]
        period = current_row['period']
        current_spend = current_row['actual_spend']
        
        result_row = {
            'ward': current_row['ward'],
            'category': current_row['category'],
            'period': period,
            'actual_spend': current_spend if current_spend is not None else 'NULL',
            'growth': 'N/A',
            'formula': 'N/A'
        }
        
        # Null value handling logic without treating as zero
        if current_spend is None:
            result_row['growth'] = 'FLAGGED: NULL SPEND'
            result_row['formula'] = 'Cannot compute on null data'
            results.append(result_row)
            continue
            
        offset = 1 if growth_type.lower() == 'mom' else 12
        
        if i >= offset:
            prev_row = data[i - offset]
            prev_spend = prev_row['actual_spend']
            
            if prev_spend is None:
                result_row['growth'] = 'FLAGGED: PREVIOUS SPEND NULL'
                result_row['formula'] = 'Cannot compute due to null in reference period'
            elif prev_spend == 0:
                result_row['growth'] = 'N/A'
                result_row['formula'] = f"({current_spend} - 0) / 0 = undefined"
            else:
                growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth_pct > 0 else ""
                result_row['growth'] = f"{sign}{growth_pct:.1f}%"
                result_row['formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
        else:
            result_row['growth'] = 'N/A'
            result_row['formula'] = 'Insufficient historical data'
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward (e.g., 'Ward 1 - Kasba')")
    parser.add_argument("--category", required=True, help="Target category")
    parser.add_argument("--growth-type", help="Growth type (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()

    # Rule: Refuse cross-ward or cross-category aggregation
    if args.ward.lower() == "all" or args.category.lower() == "all":
        print("REFUSAL: Cross-ward or cross-category aggregation is strictly prohibited. Please specify a single ward and category.")
        sys.exit(1)
        
    # Rule: Refuse if growth type not specified
    if not args.growth_type:
        print("REFUSAL: --growth-type parameter is missing. The system must not guess the formula silently.")
        sys.exit(1)

    print(f"Loading data for {args.ward} -> {args.category}...")
    try:
        data = load_dataset(args.input, args.ward, args.category)
    except Exception as e:
        print(e)
        sys.exit(1)
        
    if not data:
        print("Warning: No matching data found for the specified ward and category.")
        sys.exit(0)

    try:
        results = compute_growth(data, args.growth_type)
    except Exception as e:
        print(e)
        sys.exit(1)

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Computed per-period growth written to {args.output}")

if __name__ == "__main__":
    main()
