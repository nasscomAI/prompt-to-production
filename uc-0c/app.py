"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows."""
    data = []
    null_rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            if not row.get("actual_spend") or row.get("actual_spend").strip() == "":
                null_rows.append(row)
    
    print(f"Loaded dataset from {input_path}")
    print(f"Total null actual_spend rows: {len(null_rows)}")
    for r in null_rows:
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    if not ward or not category or not growth_type:
        print("REFUSAL: Cannot compute without explicit ward, category, and growth_type. Aggregation across wards/categories is prohibited.")
        sys.exit(1)
        
    if str(ward).lower() == "all" or str(category).lower() == "all":
        print("REFUSAL: Aggregation across all wards or categories is not allowed.")
        sys.exit(1)
        
    # Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_val = None
    
    for row in filtered:
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        if not actual_str:
            # Rule: Flag every null row before computing and report null reason from notes
            growth_str = f"Must be flagged — not computed | Reason: {notes}"
            prev_val = None # Reset prev_val since we have a gap
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "MoM Growth": growth_str
            })
            continue
            
        current = float(actual_str)
        if prev_val is None:
            growth_str = "n/a"
        else:
            diff = current - prev_val
            pct = (diff / prev_val) * 100
            sign = "+" if diff >= 0 else "−"
            
            # Rule: Show formula used in every output row alongside the result
            formula = f"(Formula: ({current} - {prev_val}) / {prev_val})"
            reason_text = f" ({notes})" if notes else ""
            
            growth_str = f"{sign}{abs(pct):.1f}%{reason_text} {formula}"
            
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": current,
            "MoM Growth": growth_str
        })
        prev_val = current
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False) # Not required so we can handle refusal explicitly
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
