import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates the expected columns, and reports the count
    of null values along with identifying the specific null rows before returning the data.
    """
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
        
    dataset = []
    expected_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    null_count = 0
    null_rows = []
    
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Check columns
        if not set(expected_columns).issubset(set(reader.fieldnames)):
            print(f"Error: Missing required columns. Expected at least: {expected_columns}")
            sys.exit(1)
            
        for row in reader:
            # Check for null in actual_spend
            actual = row['actual_spend'].strip()
            
            if actual == '' or actual.upper() == 'NULL':
                null_count += 1
                null_rows.append(row)
                row['actual_spend'] = None
            else:
                try:
                    row['actual_spend'] = float(actual)
                except ValueError:
                    row['actual_spend'] = None
                    null_count += 1
                    null_rows.append(row)
            
            dataset.append(row)

    # Report null values as required
    print(f"[Dataset Loaded] Total rows: {len(dataset)}")
    print(f"[Null Check] Found {null_count} rows with null actual_spend.")
    if null_count > 0:
        for nr in null_rows:
            notes = nr['notes'] if 'notes' in nr and nr['notes'] else "No notes"
            print(f"  -> Flagged Null Row: Period {nr['period']} | Ward {nr['ward']} | Category {nr['category']} | Reason: {notes}")

    return dataset

def compute_growth(dataset, ward, category, growth_type):
    """
    Calculates growth metrics for a given dataset segment based on a specific ward,
    category, and growth type, ensuring formulas are transparently included in the output.
    """
    # Enforcement: If --growth-type not specified - refuse and ask, never guess
    if not growth_type:
        print("Error: --growth-type must be specified (e.g., MoM). Refusing to guess.")
        sys.exit(1)
        
    # Validation against aggregation
    if not ward or not category:
        print("Error: Cannot aggregate across wards or categories. Both --ward and --category must be provided. Refusing execution.")
        sys.exit(1)
        
    # Filter dataset for specific ward and category
    filtered_data = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'.")
        return []
        
    # Sort by period to ensure chronological order
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    
    if growth_type.upper() == 'MOM':
        previous_spend = None
        
        for i in range(len(filtered_data)):
            row = filtered_data[i]
            period = row['period']
            actual = row['actual_spend']
            notes = row['notes'] if row['notes'] else ""
            
            if actual is None:
                result_row = {
                    'period': period,
                    'actual_spend': 'NULL',
                    'growth_metric': 'n/a',
                    'formula': f"Flagged null: {notes}",
                    'notes': notes
                }
                previous_spend = None
            else:
                if previous_spend is None:
                    if i > 0 and filtered_data[i-1]['actual_spend'] is None:
                        formula_str = "n/a (previous period was null)"
                    else:
                        formula_str = "n/a (first period)"
                    
                    result_row = {
                        'period': period,
                        'actual_spend': actual,
                        'growth_metric': 'n/a',
                        'formula': formula_str,
                        'notes': notes
                    }
                else:
                    try:
                        growth = (actual - previous_spend) / previous_spend
                        growth_pct = f"{growth * 100:+.1f}%"
                        # Explicitly format nicely to matching README constraints
                        formula_str = f"({actual} - {previous_spend}) / {previous_spend}"
                    except ZeroDivisionError:
                        growth_pct = "n/a"
                        formula_str = "n/a (division by zero)"
                        
                    result_row = {
                        'period': period,
                        'actual_spend': actual,
                        'growth_metric': growth_pct,
                        'formula': formula_str,
                        'notes': notes
                    }
                    
                previous_spend = actual
                
            results.append(result_row)
            
    else:
        print(f"Error: Unsupported growth type '{growth_type}'. Only 'MoM' is fully implemented in this script.")
        sys.exit(1)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate budget spend growth metrics per ward and category.")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    parser.add_argument("--ward", help="Specific municipal ward")
    parser.add_argument("--category", help="Specific budget category")
    parser.add_argument("--growth-type", help="Type of growth metric to calculate (e.g., MoM)")
    parser.add_argument("--output", help="Path to output CSV file")
    
    args = parser.parse_args()

    # Refuse aggregation explicitly if ward/category missing
    if not args.ward or not args.category:
        print("Error: Agent cannot aggregate across wards or categories. Both --ward and --category must be explicitly specified.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Error: --growth-type must be specified. Refusing to guess.")
        sys.exit(1)

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if results:
        if args.output:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                fieldnames = ['period', 'actual_spend', 'growth_metric', 'formula', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Results successfully written to {args.output}")
            
            # Print sample output if needed
            print("\nPreview of output:")
            for r in results[:3]:
                print(r)
        else:
            print("\nperiod,actual_spend,growth_metric,formula,notes")
            for r in results:
                print(f"{r['period']},{r['actual_spend']},{r['growth_metric']},\"{r['formula']}\",\"{r['notes']}\"")

if __name__ == "__main__":
    main()
