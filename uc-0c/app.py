import argparse
import csv
import sys

def load_dataset(file_path):
    """
    Reads the budget CSV file, validates required structural columns, 
    and explicitly reports the total null count and specific rows containing 
    null values before returning the data for processing.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                print(f"Error: Empty or invalid CSV file {file_path}", file=sys.stderr)
                sys.exit(1)
                
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing_cols = [c for c in required_cols if c not in headers]
            if missing_cols:
                print(f"Error: Missing required columns: {missing_cols}", file=sys.stderr)
                sys.exit(1)
                
            data = list(reader)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Find nulls (empty actual_spend or "NULL" string)
    null_rows = []
    for row in data:
        val = row.get('actual_spend', '').strip().upper()
        if not val or val == 'NULL' or val == 'NAN':
            null_rows.append(row)
            
    print(f"Dataset Validation: Found {len(null_rows)} rows with null actual_spend.")
    if len(null_rows) > 0:
        print("Specific null rows:")
        for row in null_rows:
            print(f" - Period: {row['period']}, Ward: {row['ward']}, Category: {row['category']}, Notes: {row['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates the specified growth metric for a given ward and category combination, 
    outputting a per-period table that explicitly includes the calculation formula for transparency.
    """
    # Filter by ward and category
    subset = [row for row in data if row.get('ward') == ward and row.get('category') == category]
    
    if not subset:
        print("Warning: No records found for the specified ward and category.", file=sys.stderr)
        return []
        
    # Sort by period (string sort works for YYYY-MM)
    subset.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in subset:
        actual_spend_str = row.get('actual_spend', '').strip().upper()
        notes = row.get('notes', '')
        
        result_row = {
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': '',
            'growth_metric': 'n/a',
            'formula_used': 'n/a',
            'notes': notes
        }
        
        if not actual_spend_str or actual_spend_str == 'NULL' or actual_spend_str == 'NAN':
            result_row['actual_spend'] = 'NULL'
            result_row['growth_metric'] = 'FLAGGED: NULL Value'
            result_row['formula_used'] = f"Missing data. Reason: {notes}"
            prev_spend = None # Break the series due to missing data
            results.append(result_row)
            continue
            
        try:
            actual_spend = float(actual_spend_str)
            result_row['actual_spend'] = str(actual_spend)
        except ValueError:
            result_row['actual_spend'] = actual_spend_str
            result_row['growth_metric'] = 'FLAGGED: Invalid Value'
            result_row['formula_used'] = f"Could not parse as float. Reason: {notes}"
            prev_spend = None
            results.append(result_row)
            continue
            
        if prev_spend is None:
            result_row['formula_used'] = 'No previous period data available'
        else:
            growth = ((actual_spend - prev_spend) / prev_spend) * 100
            result_row['growth_metric'] = f"{growth:+.1f}%"
            # Format formula specifically to explicitly show what went into the result
            result_row['formula_used'] = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
            
        results.append(result_row)
        prev_spend = actual_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Financial Data Analyst Agent")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Specific ward to analyze")
    parser.add_argument("--category", help="Specific category to analyze")
    parser.add_argument("--growth-type", help="Type of metric, e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    if not args.ward or args.ward.lower() == 'any' or not args.category or args.category.lower() == 'any':
        print("Refusing to aggregate: Never aggregate across wards or categories unless explicitly instructed. Please specify an exact ward and category.", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement: If --growth-type not specified — refuse and ask
    if not args.growth_type:
        print("Refusing to compute: --growth-type not specified. Please clarify growth type. I will not guess.", file=sys.stderr)
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_metric', 'formula_used', 'notes']
        try:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Computed details saved to {args.output}")
        except Exception as e:
            print(f"Error saving file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No valid results computed.")

if __name__ == "__main__":
    main()
