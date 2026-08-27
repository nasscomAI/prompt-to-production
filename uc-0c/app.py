import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the budget CSV, validates the required schema columns, and identifies all rows containing null actual_spend values.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            
            if missing_columns:
                print(f"Error: Missing columns in CSV: {', '.join(missing_columns)}")
                sys.exit(1)
            
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    null_count = 0
    print(f"Verification: Scanning for null actual_spend values...")
    for i, row in enumerate(data):
        if not row['actual_spend'] or row['actual_spend'].strip() == "":
            null_count += 1
            print(f"  Note: Row {i} ({row['period']} · {row['ward']} · {row['category']}) is null: {row['notes']}")
    
    print(f"Total nulls found: {null_count}")
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates period-over-period growth for a specific ward and category, returning a table that includes the growth percentage and the explicit formula.
    """
    # Enforcement: Refuse aggregation across wards or categories
    if not ward or ward.lower() in ["any", "all", "none"]:
        print("Refusal: All-ward aggregation or multi-ward filtering is prohibited.")
        sys.exit(1)
        
    if not category or category.lower() in ["any", "all", "none"]:
        print("Refusal: All-category aggregation or multi-category filtering is prohibited.")
        sys.exit(1)

    # Enforcement: If --growth-type not specified, refuse
    if not growth_type:
        print("Refusal: --growth-type not specified. Please specify 'MoM' or 'YoY'.")
        sys.exit(1)

    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'.")
        return []

    # Sort by period to ensure growth calculation is correct
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    
    for i in range(len(filtered_data)):
        current_row = filtered_data[i]
        period = current_row['period']
        current_spend_str = current_row['actual_spend'].strip()
        
        result = {
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': current_spend_str if current_spend_str else 'NULL',
            'growth': 'n/a',
            'formula': 'n/a',
            'notes': current_row['notes']
        }

        # MoM growth
        if i > 0:
            prev_row = filtered_data[i-1]
            prev_spend_str = prev_row['actual_spend'].strip()
            
            # Enforcement: Flag null row before computing
            if not current_spend_str:
                result['growth'] = "FLAGGED (NULL)"
                result['formula'] = f"[{current_row['notes']}]"
            elif not prev_spend_str:
                result['growth'] = "FLAGGED (NULL PREV)"
                result['formula'] = f"[{prev_row['notes']}]"
            else:
                try:
                    curr_val = float(current_spend_str)
                    prev_val = float(prev_spend_str)
                    # Math: ((Current - Prev) / Prev) * 100
                    growth_val = ((curr_val - prev_val) / prev_val) * 100
                    result['growth'] = f"{growth_val:+.1f}%"
                    
                    # Enforcement: Show formula used in every output row
                    result['formula'] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                except ValueError:
                    result['growth'] = "ERROR (Value non-numeric)"
                    result['formula'] = "n/a"
        else:
            result['growth'] = "n/a (Start of period)"
            result['formula'] = "First period in set"

        results.append(result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis App")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", help="Calculation type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    # Skill 1: load dataset
    data = load_dataset(args.input)

    # Skill 2: compute growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    if results:
        # UC requirement: Growth table saved to CSV
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        fieldnames = results[0].keys()
        try:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Success: Growth table saved to {args.output}")
        except Exception as e:
            print(f"Error writing CSV: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
