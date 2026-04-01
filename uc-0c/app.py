"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path):
    """
    Skill: load_dataset
    Reads CSV and identifies nulls.
    """
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Skill: compute_growth
    Calculates MoM growth for specific ward and category.
    """
    if growth_type != "MoM":
        print(f"Error: Growth type '{growth_type}' not supported. Only MoM is supported.")
        sys.exit(1)

    # Filter data
    filtered = [r for r in data if r['ward'] == target_ward and r['category'] == target_category]
    # Sort by period to ensure MoM is correct
    filtered.sort(key=lambda x: x['period'])

    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        period = curr['period']
        actual_spend = curr['actual_spend']
        notes = curr['notes']
        
        result_row = {
            "Ward": target_ward,
            "Category": target_category,
            "Period": period,
            "Actual Spend": actual_spend if actual_spend else "NULL",
            "MoM Growth": "n/a",
            "Formula": "n/a",
            "Flag/Note": ""
        }

        if not actual_spend:
            result_row["Flag/Note"] = f"NULL: {notes}"
            results.append(result_row)
            continue

        if prev:
            prev_spend = prev['actual_spend']
            if not prev_spend:
                result_row["MoM Growth"] = "n/a"
                result_row["Flag/Note"] = f"Cannot compute: Previous period ({prev['period']}) is NULL"
            else:
                curr_val = float(actual_spend)
                prev_val = float(prev_spend)
                growth = ((curr_val - prev_val) / prev_val) * 100
                result_row["MoM Growth"] = f"{growth:+.1f}%"
                result_row["Formula"] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
        
        results.append(result_row)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Enforcement: Refuse broad aggregation
    # If user tries to skip ward or category (though argparse makes them required), 
    # we would refuse. Here they are required.

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if results:
        fieldnames = results[0].keys()
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success! Results written to {args.output}")

if __name__ == "__main__":
    main()
