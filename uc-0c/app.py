"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    data = []
    null_count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['actual_spend'].strip():
                null_count += 1
            data.append(row)
    if null_count > 0:
        print(f"INFO: Loaded dataset with {null_count} null actual_spend rows.")
    return data

def compute_growth(ward: str, category: str, growth_type: str, dataset: list) -> list:
    if not ward or not category:
        print("REFUSAL: Cannot aggregate across wards or categories. Please specify both.")
        sys.exit(1)
        
    if growth_type not in ["MoM", "YoY"]:
        print("REFUSAL: Growth type must be explicitly specified as MoM or YoY.")
        sys.exit(1)

    # Filter data first
    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current['period']
        actual_spend_str = current['actual_spend'].strip()
        notes = current['notes'].strip()
        
        if not actual_spend_str:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "NULL",
                "growth": f"[FLAGGED] Cannot compute growth: {notes}"
            })
            continue
            
        current_val = float(actual_spend_str)
        growth_str = "n/a"
        
        if growth_type == "MoM":
            if i > 0:
                prev_str = filtered[i-1]['actual_spend'].strip()
                if prev_str:
                    prev_val = float(prev_str)
                    growth_pct = ((current_val - prev_val) / prev_val) * 100
                    sign = "+" if growth_pct > 0 else ""
                    growth_str = f"{sign}{growth_pct:.1f}% ({growth_type} formula: ({current_val} - {prev_val}) / {prev_val})"
                else:
                    growth_str = "n/a (Previous period was null)"
        elif growth_type == "YoY":
            # Just MoM implemented for this workshop context as YoY requires 2023 data
            growth_str = "n/a (YoY requires previous year data)"

        results.append({
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual_spend_str,
            "growth": growth_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=False, help="Ward to analyze")
    parser.add_argument("--category", required=False, help="Category to analyze")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    if not args.ward or not args.category:
        print("REFUSAL: Aggregation across wards or categories is not allowed. Must specify both --ward and --category.")
        sys.exit(1)
        
    if not args.growth_type:
        print("REFUSAL: Must specify --growth-type (MoM or YoY). Will not guess.")
        sys.exit(1)

    dataset = load_dataset(args.input)
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "period", "actual_spend", "growth"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
