import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads the budget CSV, validates the presence of required columns, 
    and identifies/reports the count and location of null 'actual_spend' values.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames if reader.fieldnames else []
            
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing_cols = [col for col in required_columns if col not in fieldnames]
            if missing_cols:
                print(f"Error: Missing mandatory columns: {missing_cols}")
                sys.exit(1)
                
            data = list(reader)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)
        
    # Check for nulls in actual_spend
    null_rows = []
    for row in data:
        # A value is considered null if it's empty string or whitespace, or "NULL" string
        val = row['actual_spend'].strip().upper()
        if not val or val == 'NULL':
            null_rows.append(row)
            
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend values. Flagging these rows before computation.")
        for row in null_rows:
            reason = row['notes'] if row['notes'].strip() else "Unknown"
            print(f" - Null found at Period: {row['period']}, Ward: {row['ward']}, Category: {row['category']}. Reason: {reason}")

    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates growth (e.g., MoM) for a specific ward and category combination, 
    outputting a table that includes the formula for each row.
    """
    if not growth_type:
        print("Error: --growth-type not specified. Please specify a type (e.g., MoM). Never guess.")
        sys.exit(1)
        
    if not ward or str(ward).lower() in ['all', 'any'] or not category or str(category).lower() in ['all', 'any']:
        print("Error: Never aggregate across wards or categories unless explicitly instructed. Please specify a single ward and category.")
        sys.exit(1)
        
    if growth_type.upper() not in ['MOM', 'YOY']:
        print(f"Error: Unsupported growth type '{growth_type}'. Use MoM or YoY.")
        sys.exit(1)

    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'.")
        return []
        
    # Sort chronologically by period (assuming YYYY-MM)
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered_data)):
        row = filtered_data[i]
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        is_null = not actual_str or actual_str.upper() == 'NULL'
        
        if is_null:
            growth_pct = "NULL"
            formula = f"Flagged - {notes}"
            actual_spend_out = "NULL"
        else:
            try:
                actual = float(actual_str)
            except ValueError:
                actual = actual_str
                
            actual_spend_out = actual
            
            if growth_type.upper() == 'MOM':
                if i == 0:
                    growth_pct = "n/a"
                    formula = "No previous period for MoM"
                else:
                    prev_row = filtered_data[i-1]
                    prev_actual_str = prev_row['actual_spend'].strip()
                    prev_is_null = not prev_actual_str or prev_actual_str.upper() == 'NULL'
                    
                    if prev_is_null:
                        growth_pct = "n/a"
                        formula = f"({actual} - NULL) / NULL"
                    else:
                        try:
                            prev_actual = float(prev_actual_str)
                            if prev_actual == 0:
                                growth_pct = "n/a"
                                formula = f"({actual} - 0) / 0"
                            else:
                                growth = ((actual - prev_actual) / prev_actual) * 100
                                sign = "+" if growth > 0 else ""
                                growth_pct = f"{sign}{growth:.1f}%"
                                formula = f"({actual} - {prev_actual}) / {prev_actual}"
                        except Exception:
                            growth_pct = "Error"
                            formula = "Error parsing values"
            elif growth_type.upper() == 'YOY':
                growth_pct = "n/a"
                formula = "YoY formula not fully implemented"
                
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': row['budgeted_amount'],
            'actual_spend': actual_spend_out,
            'notes': notes,
            'growth_percentage': growth_pct,
            'formula': formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Analysis Agent")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--ward", help="Target ward")
    parser.add_argument("--category", help="Target category")
    parser.add_argument("--growth-type", help="Type of growth (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    output_data = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if output_data:
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes', 'growth_percentage', 'formula']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(output_data)
            print(f"Success: Output written to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
