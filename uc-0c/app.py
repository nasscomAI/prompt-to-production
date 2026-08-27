import argparse
import csv
import os
import sys

def load_dataset(input_path):
    """
    Reads the ward budget CSV, validates column schema, and identifies null actual_spend rows.
    """
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        sys.exit(1)

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    data = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not all(col in reader.fieldnames for col in required_columns):
                print(f"Error: Missing required columns. Expected: {required_columns}")
                sys.exit(1)
            
            null_rows = []
            for i, row in enumerate(reader):
                # actual_spend might be empty string or whitespace
                raw_spend = row['actual_spend'].strip()
                if not raw_spend:
                    row['actual_spend'] = None
                    null_rows.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'reason': row['notes']
                    })
                else:
                    try:
                        row['actual_spend'] = float(raw_spend)
                    except ValueError:
                        row['actual_spend'] = None
                        null_rows.append({
                            'period': row['period'],
                            'ward': row['ward'],
                            'category': row['category'],
                            'reason': f"Invalid numeric value: {raw_spend}"
                        })
                
                # Convert budgeted_amount to float
                try:
                    row['budgeted_amount'] = float(row['budgeted_amount'])
                except ValueError:
                    row['budgeted_amount'] = 0.0
                
                data.append(row)

        # Report null values
        if null_rows:
            print(f"Found {len(null_rows)} rows with null actual_spend:")
            for nr in null_rows:
                print(f" - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
        else:
            print("No null actual_spend values found.")
            
        return data

    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    """
    Calculates period-over-period growth for a specific ward and category.
    """
    # Enforcement: Refuse aggregation
    if not ward or ward.lower() == "any" or ward.lower() == "all":
        print("Refusal: Ward must be specifically defined. Global aggregation is not permitted.")
        sys.exit(1)
    if not category or category.lower() == "any" or category.lower() == "all":
        print("Refusal: Category must be specifically defined. Global aggregation is not permitted.")
        sys.exit(1)
    if not growth_type:
        print("Refusal: Growth type (MoM or YoY) must be specified.")
        sys.exit(1)

    # Filter data
    subset = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return []

    # Sort by period
    subset.sort(key=lambda x: x['period'])

    results = []
    for i in range(len(subset)):
        curr = subset[i]
        prev = None
        
        if growth_type.upper() == 'MOM':
            if i > 0:
                prev = subset[i-1]
        elif growth_type.upper() == 'YOY':
            # Find row with same month, previous year
            curr_period = curr['period'] # YYYY-MM
            try:
                year, month = map(int, curr_period.split('-'))
                target_period = f"{year-1}-{month:02d}"
                for row in subset:
                    if row['period'] == target_period:
                        prev = row
                        break
            except:
                prev = None
        
        actual_curr = curr['actual_spend']
        actual_prev = prev['actual_spend'] if prev else None
        
        growth_val = "N/A"
        formula = "N/A"
        
        if actual_curr is None:
            growth_val = "NULL"
            formula = f"Reference value missing: {curr['notes']}"
        elif prev is None:
            growth_val = "N/A"
            formula = "First period in series"
        elif actual_prev is None:
            growth_val = "NULL"
            formula = f"Previous value missing: {prev['notes']}"
        elif actual_prev == 0:
            growth_val = "INF"
            formula = f"(({actual_curr} - 0) / 0) * 100"
        else:
            diff = actual_curr - actual_prev
            calc = (diff / actual_prev) * 100
            growth_val = f"{calc:+.1f}%"
            formula = f"(({actual_curr} - {actual_prev}) / {actual_prev}) * 100"

        results.append({
            'Ward': curr['ward'],
            'Category': curr['category'],
            'Period': curr['period'],
            'Actual Spend (₹ lakh)': "NULL" if actual_curr is None else actual_curr,
            'Growth Value': growth_val,
            'Formula': formula
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Ward Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    # Load and validate
    dataset = load_dataset(args.input)

    # Compute
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if not results:
        sys.exit(0)

    # Output to CSV
    try:
        keys = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully generated output at {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
