"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    """reads CSV, validates columns, reports null count and which rows before returning"""
    rows = []
    null_rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if not row.get("actual_spend") or row.get("actual_spend").strip() == "":
                null_rows.append((row.get("period"), row.get("ward"), row.get("category"), row.get("notes", "No notes")))
                
    if null_rows:
        print(f"Validation: Found {len(null_rows)} null actual_spend rows.")
        for nr in null_rows:
            print(f" - Null at Period: {nr[0]}, Ward: {nr[1]}, Category: {nr[2]} | Note: {nr[3]}")
    return rows

def compute_growth(rows, ward, category, growth_type):
    """takes ward + category + growth_type, returns per-period table with formula shown"""
    if not ward or not category:
        print("REFUSAL: Cannot aggregate across wards or categories. Please specify both --ward and --category.")
        sys.exit(1)
        
    if not growth_type:
        print("REFUSAL: Growth type not specified. Cannot guess (e.g., MoM or YoY).")
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"REFUSAL: Only MoM is currently implemented. You requested: {growth_type}")
        sys.exit(1)

    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        spend_str = row['actual_spend'].strip() if row['actual_spend'] else ""
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": spend_str,
            "growth": "",
            "formula": ""
        }
        
        if not spend_str:
            result_row["growth"] = "FLAGGED NULL"
            result_row["formula"] = f"Not computed (Null reason: {row.get('notes', '')})"
            prev_spend = None
        else:
            current_spend = float(spend_str)
            if prev_spend is not None:
                growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth_val > 0 else ""
                result_row["growth"] = f"{sign}{growth_val:.1f}%"
                result_row["formula"] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                result_row["growth"] = "n/a"
                result_row["formula"] = "No previous period data"
            
            prev_spend = current_spend
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth metrics written to {args.output}")

if __name__ == "__main__":
    main()
