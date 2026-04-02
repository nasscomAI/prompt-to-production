import argparse
import csv
import sys

def load_dataset(file_path):
    """
    Reads CSV and identifies null rows.
    """
    data = []
    null_count = 0
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row['actual_spend']:
                    null_count += 1
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
        
    print(f"Dataset loaded. Total rows: {len(data)}. Null actual_spend rows: {null_count}")
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Computes MoM growth for specific ward/category.
    """
    if not growth_type:
        print("Error: --growth-type must be specified (e.g., MoM).")
        sys.exit(1)
    
    if not ward or not category:
        print("Error: Both --ward and --category must be specified.")
        sys.exit(1)

    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return []

    filtered.sort(key=lambda x: x['period'])

    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        current_spend_str = row['actual_spend']
        notes = row['notes']
        
        res = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend_str if current_spend_str else "NULL",
            "growth_rate": "n/a",
            "formula": "n/a"
        }
        
        if not current_spend_str:
            res["growth_rate"] = "NULL_FLAGGED"
            res["formula"] = f"Skipped: {notes}"
            prev_spend = None
        else:
            current_spend = float(current_spend_str)
            if prev_spend is not None:
                growth = ((current_spend - prev_spend) / prev_spend) * 100
                res["growth_rate"] = f"{growth:+.1f}%"
                res["formula"] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                if prev_spend is None and period != filtered[0]['period']:
                     res["growth_rate"] = "n/a (previous null)"
                else:
                     res["growth_rate"] = "n/a (first period)"
            
            prev_spend = current_spend
            
        results.append(res)
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Auditor")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        keys = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth report written to {args.output}")
