"""
UC-0C app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath):
    data = []
    nulls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('actual_spend') or not str(row.get('actual_spend')).strip():
                nulls.append(row)
            data.append(row)
            
    print(f"Loaded {len(data)} rows.")
    if nulls:
        print(f"Flagged {len(nulls)} null rows:")
        for n in nulls:
            print(f"  - {n['period']} | {n['ward']} | {n['category']} -> Note: {n['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        print("REFUSAL: Growth type not specified. Cannot guess.")
        sys.exit(1)
        
    if not ward or ward.lower() == 'all' or not category or category.lower() == 'all':
        print("REFUSAL: Cannot aggregate across wards or categories. Specific ward and category required.")
        sys.exit(1)
        
    if growth_type.lower() != 'mom':
        print(f"REFUSAL: Unsupported growth type '{growth_type}'.")
        sys.exit(1)
        
    # Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    # Sort by period to calculate sequential growth
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        current_spend_str = row.get('actual_spend', '').strip()
        current_spend = float(current_spend_str) if current_spend_str else None
        
        growth_val = "NULL"
        formula_str = "N/A"
        
        if current_spend is None:
            growth_val = "NULL"
            formula_str = "Missing current actual_spend"
        elif prev_spend is None:
            growth_val = "NULL"
            formula_str = "No previous month data"
        else:
            growth = ((current_spend - prev_spend) / prev_spend) * 100
            sign = "+" if growth > 0 else ""
            growth_val = f"{sign}{growth:.1f}%"
            formula_str = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            
        results.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current_spend_str if current_spend_str else "NULL",
            "growth_type": growth_type,
            "growth_value": growth_val,
            "formula": formula_str,
            "notes": row["notes"]
        })
        
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth calculation type (e.g., MoM)")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        if not results:
            print("No results to write based on criteria.")
            return
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()
