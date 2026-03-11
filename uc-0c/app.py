import csv
import argparse
import os

def load_dataset(input_path):
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return []
    
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    # Pre-validation for NULLs
    null_rows = [r for r in data if not r['actual_spend'] or r['actual_spend'].strip() == ""]
    if null_rows:
        print(f"ALERT: Detected {len(null_rows)} rows with NULL actual_spend values.")
        for r in null_rows:
            print(f"  - NULL at {r['period']} | {r['ward']} | {r['category']}. Reason: {r['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    if not ward or not category:
        print("REFUSAL: Ward and Category must be specified. Aggregate calculations are prohibited.")
        return []
    
    if not growth_type:
        print("REFUSAL: Growth type not specified. Please choose MoM or YoY.")
        return []

    # Filter
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return []
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        row_result = {
            "Period": curr['period'],
            "Actual Spend": curr['actual_spend'],
            "MoM Growth": "n/a",
            "Formula": "n/a"
        }
        
        if i > 0:
            try:
                c_val = float(curr['actual_spend'])
                p_val = float(prev['actual_spend'])
                growth = ((c_val - p_val) / p_val) * 100
                row_result["MoM Growth"] = f"{growth:+.1f}%"
                row_result["Formula"] = f"(({c_val} - {p_val}) / {p_val}) * 100"
            except (ValueError, TypeError, ZeroDivisionError):
                row_result["MoM Growth"] = "NULL_FLAGGED"
                reason = curr['notes'] if not curr['actual_spend'] else prev['notes']
                row_result["Formula"] = f"Calculation stopped: Data missing. Reason: {reason}"
                
        results.append(row_result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Compute ward budget growth.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"])
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    if not data:
        return
    
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        keys = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth report saved to {args.output}")

if __name__ == "__main__":
    main()
