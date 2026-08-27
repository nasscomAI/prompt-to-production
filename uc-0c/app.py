import argparse
import csv
import os

def load_dataset(file_path):
    """
    Reads the budget CSV, validates the column structure, 
    and pre-identifies all rows with null actual_spend values.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    data = []
    null_rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Validate columns
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing required columns. Expected: {required_cols}")
            
        for i, row in enumerate(reader, start=2): # 1-indexed, starting after header
            # Parse spend
            raw_spend = row['actual_spend'].strip()
            if raw_spend == '':
                row['actual_spend'] = None
                null_rows.append((i, row['period'], row['ward'], row['category'], row['notes']))
            else:
                try:
                    row['actual_spend'] = float(raw_spend)
                except ValueError:
                    row['actual_spend'] = None
                    null_rows.append((i, row['period'], row['ward'], row['category'], "Invalid float value"))
            
            data.append(row)
            
    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    """
    Calculates MoM or YoY expenditure growth for a filtered ward and category.
    """
    # Filter
    subset = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        return []
        
    # Sort by period
    subset.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(subset):
        period = row['period']
        actual = row['actual_spend']
        result_row = {
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual if actual is not None else "NULL",
            'mom_growth': "n/a",
            'formula': "n/a",
            'notes': row['notes']
        }
        
        # Calculate MoM growth
        if growth_type == 'MoM' and i > 0:
            prev_row = subset[i-1]
            prev_actual = prev_row['actual_spend']
            
            if actual is not None and prev_actual is not None and prev_actual != 0:
                growth = (actual - prev_actual) / prev_actual
                result_row['mom_growth'] = f"{growth:+.1%}"
                result_row['formula'] = f"({actual} - {prev_actual}) / {prev_actual}"
            elif actual is None:
                result_row['mom_growth'] = f"NULL ({row['notes']})"
                result_row['formula'] = "Error: Current row missing"
            elif prev_actual is None:
                result_row['mom_growth'] = f"NULL ({prev_row['notes']})"
                result_row['formula'] = "Error: Previous row missing"
                
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target category name")
    parser.add_argument("--growth-type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output summary")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: Refuse if growth-type missing
    if not args.growth_type:
        print("REFUSAL: Growth type (--growth-type) is mandatory. Please specify MoM or YoY.")
        return

    # Enforcement Rule 1: Never aggregate across wards or categories
    if not args.ward or not args.category:
        print("REFUSAL: Ward and Category must be explicitly specified to prevent unauthorized aggregation.")
        return

    try:
        data, null_rows = load_dataset(args.input)
        
        # Enforcement Rule 2: Report null rows to console
        if null_rows:
            print(f"INFO: Identified {len(null_rows)} rows with null values.")
            # Optional: only report if related to target ward/category? 
            # README says "Flag every null row before computing"
            for row_info in null_rows:
                print(f"  - Row {row_info[0]}: {row_info[1]} | {row_info[2]} | {row_info[3]} -> {row_info[4]}")

        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"WARNING: No data found for Ward '{args.ward}' and Category '{args.category}'.")
            return

        # Save to CSV
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            
        print(f"Success: Analysis saved to {args.output}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
