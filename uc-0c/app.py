"""
UC-0C app.py — Budget Growth Analyst
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Calculates growth metrics while enforcing granularity and handling nulls explicitly.
"""
import argparse
import csv
import os

def load_dataset(input_path):
    """
    Skill: load_dataset
    Reads CSV, identifies null rows, and generates an inventory report.
    """
    data = []
    null_entries = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row['actual_spend'].strip()
            if not val:
                row['actual_spend'] = None
                null_entries.append({
                    "period": row['period'],
                    "ward": row['ward'],
                    "category": row['category'],
                    "reason": row['notes']
                })
            else:
                row['actual_spend'] = float(val)
            data.append(row)
    
    print(f"Dataset loaded: {len(data)} rows.")
    print(f"Null Inventory found {len(null_entries)} entries:")
    for entry in null_entries:
        print(f"- {entry['period']} | {entry['ward']} | {entry['category']} | Reason: {entry['reason']}")
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates growth (MoM) for a specific ward and category with formula traces.
    """
    # Enforcement Rule 1: No unauthorized aggregation
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    if not filtered:
        print(f"Error: No data found for Ward: {ward} | Category: {category}")
        return []

    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend']
        
        res_row = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual if actual is not None else "NULL",
            "growth_pct": "n/a",
            "formula": "n/a"
        }
        
        if i > 0:
            prev_row = filtered[i-1]
            prev_actual = prev_row['actual_spend']
            
            # Enforcement Rule 2: Explicit Null Handling
            if actual is None:
                res_row['growth_pct'] = "FLAGGED"
                res_row['formula'] = f"NULL: {row['notes']}"
            elif prev_actual is None:
                res_row['growth_pct'] = "FLAGGED"
                res_row['formula'] = f"PREV NULL ({prev_row['period']}): {prev_row['notes']}"
            else:
                # Enforcement Rule 3: Formula Transparency
                growth = ((actual - prev_actual) / prev_actual) * 100
                res_row['growth_pct'] = f"{growth:+.1f}%"
                res_row['formula'] = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
        
        results.append(res_row)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific budget category")
    parser.add_argument("--growth-type", help="MoM or YoY (Required)")
    parser.add_argument("--output", required=True, help="Path to output growth_output.csv")
    args = parser.parse_args()

    # Enforcement Rule 4: Verify growth-type
    if not args.growth_type:
        print("Refusal: --growth-type is required. Please specify MoM or YoY.")
        return

    # Enforcement Rule 1: Refuse multi-ward/multi-category aggregation
    if args.ward.lower() in ["any", "all", "*", "total"] or \
       args.category.lower() in ["any", "all", "*", "total"]:
        print("Refusal: Cross-ward or cross-category aggregation is prohibited. System must maintain granularity.")
        return

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        return

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth calculation complete. Saved to {args.output}")

if __name__ == "__main__":
    main()
