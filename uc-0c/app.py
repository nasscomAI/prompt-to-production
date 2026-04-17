import argparse
import csv

def load_dataset(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(ward, category, growth_type, data):
    if growth_type != "MoM":
        return None, "Error: Only MoM growth type is supported. Please specify --growth-type MoM."
    
    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    # Sort by period to be safe
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        current_spend_str = row['actual_spend'].strip()
        notes = row['notes']
        
        if not current_spend_str:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "n/a",
                "formula": "n/a",
                "status": f"FLAG: {notes}"
            })
            prev_spend = None # Break the chain for next MoM
            continue
            
        current_spend = float(current_spend_str)
        
        if prev_spend is None:
            results.append({
                "period": period,
                "actual_spend": current_spend,
                "growth": "n/a",
                "formula": "First period or previous was NULL",
                "status": "OK"
            })
        else:
            growth = ((current_spend - prev_spend) / prev_spend) * 100
            formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            results.append({
                "period": period,
                "actual_spend": current_spend,
                "growth": f"{growth:+.1f}%",
                "formula": formula,
                "status": "OK"
            })
            
        prev_spend = current_spend
        
    return results, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False) # Optional to test the "refusal" rule
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results, error = compute_growth(args.ward, args.category, args.growth_type, data)
    
    if error:
        print(error)
    else:
        keys = ["period", "actual_spend", "growth", "formula", "status"]
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth report generated: {args.output}")
