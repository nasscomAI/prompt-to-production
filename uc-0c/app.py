import argparse
import csv
import sys

def load_dataset(input_path):
    rows = []
    nullCount = 0
    nullRows = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2): # 1 is header
                rows.append(row)
                if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                    nullCount += 1
                    notes = row.get("notes", "No notes provided")
                    nullRows.append(f"Row {i} (Period: {row['period']}, Ward: {row['ward']}, Category: {row['category']}) - Reason: {notes}")
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    print(f"Dataset loaded. Found {len(rows)} rows.")
    if nullCount > 0:
        print(f"WARNING: Found {nullCount} deliberately null 'actual_spend' values:")
        for nr in nullRows:
            print(f" - {nr}")
            
    return rows

def compute_growth(rows, target_ward, target_category, growth_type):
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not target_ward or target_ward.lower() in ['any', 'all', '']:
        print("ERROR: System REFUSES to aggregate across wards. You must explicitly specify a ward.")
        sys.exit(1)
    if not target_category or target_category.lower() in ['any', 'all', '']:
        print("ERROR: System REFUSES to aggregate across categories. You must explicitly specify a category.")
        sys.exit(1)
        
    # Rule 4: If growth_type not specified - refuse and ask, never guess
    if not growth_type:
        print("ERROR: System REFUSES to compute. --growth-type was not specified. Please re-run with --growth-type (e.g., MoM or YoY).")
        sys.exit(1)

    filtered = [r for r in rows if r['ward'] == target_ward and r['category'] == target_category]
    # sort by period
    filtered.sort(key=lambda x: x['period'])

    results = []
    
    for i in range(len(filtered)):
        curr_row = filtered[i]
        period = curr_row['period']
        actual_spend = curr_row['actual_spend'].strip()
        
        # Rule 2: Flag every null row before computing
        if not actual_spend:
            reason = curr_row.get("notes", "No reason provided")
            results.append({
                "Ward": target_ward,
                "Category": target_category,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "Growth": "FLAGGED: NULL VALUE",
                "Formula": f"Cannot compute. Notes: {reason}"
            })
            continue
            
        curr_val = float(actual_spend)
        
        prev_val = None
        prev_period = ""
        jump = 1 if growth_type.lower() == 'mom' else 12
        if i >= jump:
            prev_spend_str = filtered[i-jump]['actual_spend'].strip()
            if prev_spend_str:
                prev_val = float(prev_spend_str)
                prev_period = filtered[i-jump]['period']
                
        if prev_val is None:
            results.append({
                "Ward": target_ward,
                "Category": target_category,
                "Period": period,
                "Actual Spend (₹ lakh)": curr_val,
                "Growth": "n/a",
                "Formula": f"No previous {growth_type} data for comparison."
            })
        else:
            growth_pct = ((curr_val - prev_val) / prev_val) * 100
            # formatting
            sign = "+" if growth_pct > 0 else ""
            growth_str = f"{sign}{growth_pct:.1f}%"
            # Rule 3: Show formula used in every output row
            formula_str = f"({curr_val} - {prev_val}) / {prev_val} * 100 = {growth_str} ({growth_type} vs {prev_period})"
            
            results.append({
                "Ward": target_ward,
                "Category": target_category,
                "Period": period,
                "Actual Spend (₹ lakh)": curr_val,
                "Growth": growth_str,
                "Formula": formula_str
            })
            
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)  
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "Growth", "Formula"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Successfully computed growth and saved to {args.output}")

if __name__ == "__main__":
    main()
