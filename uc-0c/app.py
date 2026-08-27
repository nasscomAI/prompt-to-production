"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import sys

def load_dataset(input_path):
    rows = []
    null_count = 0
    null_details = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                spend = row.get('actual_spend', '').strip()
                if not spend or spend.lower() == 'null':
                    null_count += 1
                    notes = row.get('notes', 'No notes provided')
                    period = row.get('period', 'Unknown')
                    ward = row.get('ward', 'Unknown')
                    null_details.append(f"{period} in {ward}: {notes}")
                rows.append(row)
                
        print(f"Dataset loaded. Discovered {null_count} total null rows.")
        for detail in null_details:
            print(f" -> NULL Row: {detail}")
            
        return rows
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        sys.exit(1)

def compute_growth(rows, ward, category, growth_type):
    # Rule 1: Refuse aggregation unless explicitly scoped
    if not ward or not category:
        print("REFUSAL: Cannot aggregate across wards or categories. Please explicitly define --ward and --category.")
        sys.exit(1)
        
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    
    # Sort by period explicitly to guarantee correct MoM logic
    filtered.sort(key=lambda x: x.get('period', ''))
    
    output = []
    prev_spend = None
    
    for i, row in enumerate(filtered):
        period = row.get('period')
        spend_str = row.get('actual_spend', '').strip()
        
        # Rule 2: Flag Nulls
        if not spend_str or spend_str.lower() == 'null':
            notes = row.get('notes', 'No notes provided')
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": f"Flagged Null: {notes}"
            })
            prev_spend = None # Break sequence so next month doesn't compare against null
            continue
            
        try:
            curr_spend = float(spend_str)
        except ValueError:
            prev_spend = None
            continue
            
        if prev_spend is None:
            growth = "n/a"
            formula = "n/a (no previous period)"
        else:
            if growth_type.lower() == 'mom':
                if prev_spend == 0:
                    growth = "n/a"
                    formula = "Division by zero"
                else:
                    g = ((curr_spend - prev_spend) / prev_spend) * 100
                    # Standard formatting
                    sign = "+" if g > 0 else ""
                    growth = f"{sign}{g:.1f}%"
                    
                    # Rule 3: Show formula
                    formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"
            else:
                growth = "Unsupported type"
                formula = "Check growth_type"
                
        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": curr_spend,
            "growth": growth,
            "formula": formula
        })
        
        prev_spend = curr_spend
        
    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")
    parser.add_argument("--input", required=True, help="Path to csv data")
    parser.add_argument("--ward", required=False, help="Explicit ward filter to prevent aggregation")
    parser.add_argument("--category", required=False, help="Explicit category filter to prevent aggregation")
    parser.add_argument("--growth-type", required=False, help="Must be specified (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output csv path")
    
    args = parser.parse_args()
    
    # Rule 4: Never guess if missing
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. I cannot assume a formula. Please specify.")
        sys.exit(1)
        
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            if not results:
                print("No data matched the filter.")
                sys.exit(0)
            writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Success! Output written to {args.output}")
    except Exception as e:
        print(f"Error writing to output: {e}")

if __name__ == "__main__":
    main()
