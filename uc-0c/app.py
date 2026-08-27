import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    data = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers or not all(col in headers for col in required_columns):
            raise ValueError(f"Invalid columns. Expected: {required_columns}")
        
        for row_idx, row in enumerate(reader, start=2): # 1 is header
            data.append(row)
            if not row['actual_spend'].strip():
                null_rows.append({
                    "row_num": row_idx,
                    "period": row['period'],
                    "ward": row['ward'],
                    "category": row['category'],
                    "notes": row['notes']
                })
                
    if null_rows:
        print(f"Dataset loaded. Found {len(null_rows)} null values in 'actual_spend'.")
        print("The following rows have null 'actual_spend' and must be flagged:")
        for nr in null_rows:
            print(f" - {nr['period']} · {nr['ward']} · {nr['category']}: {nr['notes']}")
    else:
        print("Dataset loaded. 0 null values found.")
        
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type not specified. Please explicitly state the calculation method (e.g., MoM), I will not guess.")
        
    if (target_ward and target_ward.lower() == "any") or (target_category and target_category.lower() == "any"):
        raise ValueError("REFUSAL: Aggregating across wards or categories is strictly forbidden unless explicitly instructed. Please specify a single ward and category, or omit to compute all independently.")
        
    # Find all unique ward/category pairs to process
    pairs = set()
    for row in data:
        w = row['ward']
        c = row['category']
        if (not target_ward or w == target_ward) and (not target_category or c == target_category):
            pairs.add((w, c))
            
    results = []
    
    if growth_type.upper() == "MOM":
        growth_col_name = "MoM Growth"
        for w, c in sorted(list(pairs)):
            # Filter and sort data for this specific ward and category
            filtered = [r for r in data if r['ward'] == w and r['category'] == c]
            filtered.sort(key=lambda x: x['period'])
            
            for i in range(len(filtered)):
                current_row = filtered[i]
                period = current_row['period']
                actual = current_row['actual_spend'].strip()
                notes = current_row['notes'].strip()
                
                if not actual:
                    # Rule 2: Flag every null row before computing — report null reason from the notes column
                    results.append({
                        "Ward": w,
                        "Category": c,
                        "Period": period,
                        "Actual Spend (₹ lakh)": "NULL",
                        growth_col_name: "Must be flagged — not computed",
                        "Formula": "n/a",
                        "Notes": notes
                    })
                    continue
                    
                actual_val = float(actual)
                
                if i == 0:
                    results.append({
                        "Ward": w,
                        "Category": c,
                        "Period": period,
                        "Actual Spend (₹ lakh)": f"{actual_val}",
                        growth_col_name: "n/a",
                        "Formula": "n/a",
                        "Notes": ""
                    })
                else:
                    prev_row = filtered[i-1]
                    prev_actual = prev_row['actual_spend'].strip()
                    if not prev_actual:
                        results.append({
                            "Ward": w,
                            "Category": c,
                            "Period": period,
                            "Actual Spend (₹ lakh)": f"{actual_val}",
                            growth_col_name: "Cannot compute (previous month NULL)",
                            "Formula": f"({actual_val} - NULL) / NULL",
                            "Notes": ""
                        })
                    else:
                        prev_val = float(prev_actual)
                        if prev_val == 0:
                             growth_pct = "n/a"
                             formula = f"({actual_val} - 0) / 0"
                        else:
                             growth = (actual_val - prev_val) / prev_val
                             growth_pct_val = growth * 100
                             sign = "+" if growth_pct_val > 0 else ""
                             growth_pct = f"{sign}{growth_pct_val:.1f}%"
                             formula = f"({actual_val} - {prev_val}) / {prev_val} * 100"
                        
                        results.append({
                            "Ward": w,
                            "Category": c,
                            "Period": period,
                            "Actual Spend (₹ lakh)": f"{actual_val}",
                            growth_col_name: growth_pct,
                            "Formula": formula,
                            "Notes": ""
                        })
    else:
        raise ValueError(f"REFUSAL: Growth type '{growth_type}' is not supported yet or cannot be computed.")
        
    return results, growth_col_name if growth_type.upper() == "MOM" else "Growth"

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=False, help="Specific ward name")
    parser.add_argument("--category", required=False, help="Specific category")
    parser.add_argument("--growth-type", required=False, help="Type of growth calculation (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write the output CSV")
    args = parser.parse_args()

    try:
        data = load_dataset(args.input)
        
        # Enforce arguments
        if (args.ward and args.ward.lower() == "any") or (args.category and args.category.lower() == "any"):
             print("Error: REFUSAL: --ward and --category 'any' indicates aggregation. Aggregation across wards or categories is not allowed.")
             sys.exit(1)
             
        if not args.growth_type:
             print("REFUSAL: --growth-type must be specified. I will not guess the calculation method.")
             try:
                 args.growth_type = input("Please specify growth type (e.g. MoM): ").strip()
                 if not args.growth_type:
                     sys.exit("Error: No calculation method provided.")
             except (EOFError, KeyboardInterrupt):
                 sys.exit("\nError: No calculation method provided.")
        
        results, growth_col_name = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
             print(f"Warning: No data found for Ward: '{args.ward}' and Category: '{args.category}'")
             
        # Write to output
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not results:
                writer = csv.writer(f)
                writer.writerow(["No data"])
            else:
                fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", growth_col_name, "Formula", "Notes"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in results:
                    writer.writerow(r)
                    
        print(f"Success: Growth computed and written to {args.output}")

    except Exception as e:
        print(f"Error processing dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
