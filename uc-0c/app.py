import argparse
import csv
import sys

def load_dataset(filepath):
    """reads CSV, validates columns, reports null count and which rows before returning"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not reader.fieldnames or not expected_cols.issubset(set(reader.fieldnames)):
                print("Error: Dataset format does not match expected ward budget schema.")
                sys.exit(1)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    null_rows = [r for r in data if not r.get('actual_spend')]
    print(f"Dataset successfully loaded. Identified {len(null_rows)} explicitly null 'actual_spend' records:")
    for row in null_rows:
        note = row.get('notes') if row.get('notes') else "No explanation provided"
        print(f" - Period: {row.get('period')}, Ward: {row.get('ward')}, Category: {row.get('category')} | Reason: {note}")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """takes ward + category + growth_type, returns per-period table with formula shown"""
    if not growth_type:
        print("REFUSAL: Growth type not explicitly specified. Refusing to guess.")
        sys.exit(1)
        
    if not ward or not category:
        print("REFUSAL: Refusing to aggregate across multiple wards or categories without explicit instruction.")
        sys.exit(1)
        
    filtered = [r for r in data if r.get('ward') == ward and r.get('category') == category]
    filtered.sort(key=lambda x: x.get('period', ''))
    
    if not filtered:
        print(f"No data found for Ward '{ward}' and Category '{category}'.")
        sys.exit(1)
        
    results = []
    
    if growth_type.lower() == "mom":
        for i, row in enumerate(filtered):
            period = row.get('period')
            curr_spend_str = row.get('actual_spend')
            
            if not curr_spend_str:
                note = row.get('notes') if row.get('notes') else 'Missing data'
                results.append({
                    "Ward": row.get('ward'),
                    "Category": row.get('category'),
                    "Period": period,
                    "Actual Spend": "NULL",
                    "MoM Growth": f"Flagged: {note}",
                    "Formula": "n/a"
                })
                continue
                
            curr_spend = float(curr_spend_str)
            
            if i == 0:
                results.append({
                    "Ward": row.get('ward'),
                    "Category": row.get('category'),
                    "Period": period,
                    "Actual Spend": curr_spend,
                    "MoM Growth": "N/A",
                    "Formula": "First period in dataset sequence"
                })
                continue
                
            prev_row = filtered[i-1]
            prev_spend_str = prev_row.get('actual_spend')
            
            if not prev_spend_str:
                results.append({
                    "Ward": row.get('ward'),
                    "Category": row.get('category'),
                    "Period": period,
                    "Actual Spend": curr_spend,
                    "MoM Growth": "N/A",
                    "Formula": "Previous period is null"
                })
            else:
                prev_spend = float(prev_spend_str)
                growth_val = ((curr_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth_val > 0 else ""
                results.append({
                    "Ward": row.get('ward'),
                    "Category": row.get('category'),
                    "Period": period,
                    "Actual Spend": curr_spend,
                    "MoM Growth": f"{sign}{growth_val:.1f}%",
                    "Formula": f"({curr_spend} - {prev_spend}) / {prev_spend} * 100"
                })
    else:
        print(f"REFUSAL: Unsupported or unhandled growth type '{growth_type}'.")
        sys.exit(1)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Ward Budget Analyst")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", default=None, help="Specific ward to analyze")
    parser.add_argument("--category", default=None, help="Specific category to analyze")
    parser.add_argument("--growth-type", default=None, help="Growth calculation methodology")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    # Apply skills sequentially
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save output
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not results:
                return
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Output correctly resolved and written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
