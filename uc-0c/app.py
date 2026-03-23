"""
UC-0C — Budgetary Growth Analyst
Built using the RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os

def load_dataset(file_path):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    
    data = []
    null_rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            # Check for null actual_spend
            if not row['actual_spend'].strip():
                null_rows.append({
                    "line": i,
                    "period": row['period'],
                    "ward": row['ward'],
                    "category": row['category'],
                    "reason": row['notes']
                })
            data.append(row)
            
    print(f"Dataset loaded. Total rows: {len(data)}")
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend values:")
        for nr in null_rows:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} -> Reason: {nr['reason']}")
            
    return data, null_rows

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses cross-ward/cross-category aggregation.
    """
    # 1. Filter data
    filtered = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]
    
    if not filtered:
        return []
    
    # Sort by period to ensure growth calculation is correct
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        row = filtered[i]
        actual = row['actual_spend'].strip()
        period = row['period']
        
        result_row = {
            "Period": period,
            "Ward": target_ward,
            "Category": target_category,
            "Actual Spend": actual if actual else "NULL",
            "Growth": "n/a",
            "Formula": "n/a"
        }
        
        if not actual:
            result_row["Growth"] = "FLAGGED"
            result_row["Formula"] = f"NULL: {row['notes']}"
        elif i > 0:
            prev_row = filtered[i-1]
            prev_actual = prev_row['actual_spend'].strip()
            
            if prev_actual:
                curr_val = float(actual)
                prev_val = float(prev_actual)
                growth = ((curr_val - prev_val) / prev_val) * 100
                result_row["Growth"] = f"{growth:+.1f}%"
                result_row["Formula"] = f"({curr_val} - {prev_val}) / {prev_val}"
            else:
                result_row["Growth"] = "n/a"
                result_row["Formula"] = "Previous period data is NULL"
        else:
            result_row["Formula"] = "First period in sequence"
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budgetary Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    # RICE Enforcement: If growth-type not MoM or YoY, we handle it
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Error: Unsupported growth type '{args.growth_type}'. Only MoM and YoY are supported.")
        return

    try:
        data, null_rows = load_dataset(args.input)
        
        # Calculate growth
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"No data found for Ward: {args.ward}, Category: {args.category}")
            return
            
        # Write results
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Done. Growth analysis written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
