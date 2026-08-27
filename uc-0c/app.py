import argparse
import csv
import os

def load_dataset(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        return "Error: Growth type not specified. Please choose MoM or YoY."
    
    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        return f"Error: No data found for Ward: {ward} and Category: {category}."
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered_data:
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row['notes']
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend if actual_spend else "NULL",
            "growth": "n/a",
            "formula": "n/a",
            "notes": notes
        }
        
        if not actual_spend:
            result_row["growth"] = "NULL"
            result_row["formula"] = f"Calculation skipped: {notes}"
            prev_spend = None # Break the chain for MoM if null
        else:
            current_spend = float(actual_spend)
            if prev_spend is not None:
                if growth_type == "MoM":
                    growth = ((current_spend - prev_spend) / prev_spend) * 100
                    result_row["growth"] = f"{growth:+.1f}%"
                    result_row["formula"] = f"MoM = ({current_spend} - {prev_spend}) / {prev_spend}"
            
            prev_spend = current_spend
            
        results.append(result_row)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess.")
        return

    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if isinstance(results, str):
            print(results)
            return

        keys = results[0].keys()
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"Results written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
