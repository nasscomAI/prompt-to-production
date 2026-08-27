import argparse
import csv
import sys

def load_dataset(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames or not all(c in fieldnames for c in ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']):
                print("Error: Invalid schema. Missing required columns.")
                sys.exit(1)
                
            data = list(reader)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    null_rows = []
    for idx, row in enumerate(data):
        spend_val = row.get('actual_spend', '').strip()
        if not spend_val:
            null_rows.append(row)
            
    print(f"Dataset loaded. Total rows: {len(data)}")
    if null_rows:
        print(f"Flagged: Found {len(null_rows)} deliberate null actual_spend values.")
        for r in null_rows:
            reason = r.get('notes', 'No reason provided').strip()
            print(f" - Period: {r['period']}, Ward: {r['ward']}, Category: {r['category']} | Reason: {reason}")
            
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    # Enforcement: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        print("Refusal: --growth-type not specified. Cannot intuitively guess the formula. Please specify (e.g., MoM).")
        sys.exit(1)
        
    if growth_type.upper() not in ["MOM", "YOY"]:
        print(f"Refusal: Unknown growth type '{growth_type}'. Only MoM and YoY are supported.")
        sys.exit(1)
        
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    if target_ward.lower() in ["any", "all", ""] or target_category.lower() in ["any", "all", ""]:
        print("Refusal: System cannot safely aggregate across multiple wards or categories. Refusing request.")
        sys.exit(1)
        
    filtered = [d for d in data if d['ward'].strip().lower() == target_ward.strip().lower() 
                and d['category'].strip().lower() == target_category.strip().lower()]
                
    if not filtered:
        print(f"Warning: No data found for Ward: '{target_ward}' and Category: '{target_category}'")
        return []

    # Sort sequentially by period to assure correct relative indexing
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row.get('notes', '').strip()
        
        ward_val = row['ward']
        cat_val = row['category']
        
        # Enforcement: Flag every null row before computing
        if not actual_str:
            spend_out = "NULL"
            growth_out = f"Must be flagged — not computed. Reason: {notes}"
        else:
            spend_out = actual_str
            curr_val = float(actual_str)
            
            # Determine previous value based on growth_type
            prev_row = None
            if growth_type.upper() == "MOM":
                if i > 0:
                    prev_row = filtered[i-1]
            elif growth_type.upper() == "YOY":
                curr_year, curr_month = period.split('-')
                prev_period = f"{int(curr_year)-1}-{curr_month}"
                for fr in filtered:
                    if fr['period'] == prev_period:
                        prev_row = fr
                        break
                        
            if prev_row is None:
                growth_out = "N/A (no previous period)"
            elif not prev_row['actual_spend'].strip():
                growth_out = "N/A (previous period NULL)"
            else:
                prev_val = float(prev_row['actual_spend'])
                growth_pct = ((curr_val - prev_val) / prev_val) * 100
                sign = "+" if growth_pct > 0 else "−" if growth_pct < 0 else ""
                growth_str = f"{sign}{abs(growth_pct):.1f}%"
                
                # Enforcement: Show formula used in every output row alongside the result
                formula_str = f"({curr_val} - {prev_val}) / {prev_val}"
                growth_out = f"{growth_str} (formula: {formula_str})"
                
        results.append({
            "Ward": ward_val,
            "Category": cat_val,
            "Period": period,
            "Actual Spend (₹ lakh)": spend_out,
            f"{growth_type} Growth": growth_out
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget data CSV")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", default=None, help="Growth type (e.g. MoM or YoY). Made optional to test refusal logic.")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        # Determine growth_type header safely
        growth_header = f"{args.growth_type} Growth" if args.growth_type else "Growth"
        
        try:
            with open(args.output, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", growth_header]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in results:
                    writer.writerow(r)
            print(f"Success! Output cleanly formatted and written to {args.output}")
        except Exception as e:
            print(f"Error writing to output: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
