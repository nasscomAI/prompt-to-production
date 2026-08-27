import csv
import argparse
import os

def load_dataset(input_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    
    data = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(data, ward, category, growth_type):
    # Rule 1: No aggregation across wards/categories
    if not ward or not category:
        return "ERROR: Ward and Category must be specified. Aggregation not permitted."
    
    if growth_type != "MoM":
        return f"ERROR: Growth type '{growth_type}' is not supported. Use MoM."

    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period to ensure order
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual = row['actual_spend']
        notes = row['notes']
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual else "NULL",
            "growth": "n/a",
            "formula": "n/a",
            "status": "OK"
        }
        
        if not actual:
            result_row["growth"] = "NULL"
            result_row["formula"] = "n/a"
            result_row["status"] = f"FLAGGED: {notes}"
            prev_spend = None # Cannot compute next growth from null
        else:
            curr_spend = float(actual)
            if prev_spend is not None:
                growth = ((curr_spend - prev_spend) / prev_spend) * 100
                result_row["growth"] = f"{growth:+.1f}%"
                result_row["formula"] = f"({curr_spend} - {prev_spend}) / {prev_spend}"
            else:
                result_row["growth"] = "n/a"
                result_row["formula"] = "First month in series"
            
            prev_spend = curr_spend
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--growth-type", default=None)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    # Enforcement Rules
    if args.ward is None or args.category is None:
        print("REFUSAL: All-ward or all-category aggregation is not permitted. Please specify both.")
        return
        
    if args.growth_type is None:
        print("REFUSAL: Growth type (--growth-type) is missing. Please specify 'MoM'.")
        return

    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if isinstance(results, str):
            print(results)
            return
            
        keys = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth report successfully saved to {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
