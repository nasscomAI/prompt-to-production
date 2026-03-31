import argparse
import csv

def load_dataset(file_path):
    """
    Reads the budget CSV and returns the data.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(ward, category, growth_type, data):
    """
    Calculates MoM growth for a specific ward and category.
    """
    # Filter and sort data
    subset = [r for r in data if r['ward'] == ward and r['category'] == category]
    subset.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(subset)):
        curr = subset[i]
        curr_val = curr['actual_spend']
        curr_period = curr['period']
        
        if i == 0:
            results.append({
                "period": curr_period,
                "actual_spend": curr_val if curr_val else "NULL",
                "growth": "n/a",
                "formula": "First period in dataset"
            })
            continue
            
        prev = subset[i-1]
        prev_val = prev['actual_spend']
        
        # Check for nulls
        if not curr_val:
            results.append({
                "period": curr_period,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": f"NULL in current period: {curr['notes']}"
            })
        elif not prev_val:
            results.append({
                "period": curr_period,
                "actual_spend": curr_val,
                "growth": "FLAGGED",
                "formula": f"NULL in previous period: {prev['notes']}"
            })
        else:
            c = float(curr_val)
            p = float(prev_val)
            growth = ((c - p) / p) * 100
            sign = "+" if growth >= 0 else ""
            results.append({
                "period": curr_period,
                "actual_spend": curr_val,
                "growth": f"{sign}{growth:.1f}%",
                "formula": f"({c} - {p}) / {p}"
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type (MoM or YoY) must be specified. Aggregate calculations are prohibited.")
        return

    data = load_dataset(args.input)
    results = compute_growth(args.ward, args.category, args.growth_type, data)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Growth output written to {args.output}")

if __name__ == "__main__":
    main()
