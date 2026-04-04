"""
UC-0C app.py — Starter file completed.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(input_path, ward, category):
    """reads CSV, validates columns, reports null count"""
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        
    filtered = []
    null_count = 0
    for row in data:
        if row['ward'] == ward and row['category'] == category:
            filtered.append(row)
        if not row.get('actual_spend', '').strip():
            null_count += 1
            
    print(f"Dataset loaded. Global nulls detected: {null_count}")
    return sorted(filtered, key=lambda x: x['period'])

def compute_growth(data, growth_type):
    """takes metrics, returns per-period table with formula shown"""
    if not growth_type:
        sys.exit("Error: Refusal condition triggered. --growth-type not specified (cannot guess).")
    if growth_type.upper() != "MOM":
        sys.exit(f"Error: Unsupported growth type {growth_type}.")
        
    results = []
    prev_val = None
    
    for row in data:
        period = row['period']
        notes = row.get('notes', '').strip()
        spend_str = row.get('actual_spend', '').strip()
        
        if not spend_str:
            results.append({
                "period": period,
                "ward": row['ward'],
                "category": row['category'],
                "actual_spend": "NULL",
                "mom_growth": f"Must be flagged — {notes} - not computed"
            })
            prev_val = None  # Reset computation chain
            continue
            
        val = float(spend_str)
        if prev_val is None:
            growth_info = "n/a (no prior data)"
        else:
            pct = ((val - prev_val) / prev_val) * 100
            sign = "+" if pct > 0 else ""
            formula = f"formula: ({val} - {prev_val}) / {prev_val}"
            growth_info = f"{sign}{pct:.1f}% ({formula})"
            if notes:
                growth_info += f" ({notes})"
                
        results.append({
            "period": period,
            "ward": row['ward'],
            "category": row['category'],
            "actual_spend": val,
            "mom_growth": growth_info
        })
        prev_val = val
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward strictly required")
    parser.add_argument("--category", required=True, help="Specific category strictly required")
    parser.add_argument("--growth-type", required=False, help="Explicitly requested growth formula")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    if args.ward.lower() in ["all", "any"] or args.category.lower() in ["all", "any"]:
        sys.exit("Error: Agents.md enforcement 1: Never aggregate across wards or categories unless explicitly instructed.")
        
    # App logic mimicking perfect agent behavior
    data = load_dataset(args.input, args.ward, args.category)
    results = compute_growth(data, args.growth_type)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "period", "actual_spend", "mom_growth"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Computed safe per-row output. Wrote to {args.output}")

if __name__ == "__main__":
    main()
