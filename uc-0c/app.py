import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """Read CSV, validate columns, and track nulls."""
    data = []
    nulls_found = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing required columns. Found: {reader.fieldnames}")
            
        for row in reader:
            data.append(row)
            if not row['actual_spend'].strip():
                nulls_found.append(row)
                
    print(f"[LOG] Loaded {len(data)} rows. Found {len(nulls_found)} rows with NULL actual_spend.")
    return data

def compute_growth(data: list, target_ward: str, target_category: str, growth_type: str, output_path: str):
    """Enforce strict ward/category scoping and flag nulls."""
    
    # ENFORCEMENT 1: Refuse missing Growth Type
    if not growth_type:
        print("[REFUSAL] Missing --growth-type parameter. Cannot guess (e.g., MoM vs YoY). Exiting.")
        sys.exit(1)
        
    if growth_type not in ["MoM"]:  # Simplified for the UC
        print(f"[REFUSAL] Unsupported growth type: {growth_type}")
        sys.exit(1)

    # ENFORCEMENT 2: Refuse cross-ward/cross-category aggregation
    if not target_ward or not target_category:
        print("[REFUSAL] Missing --ward or --category. Aggregation across scopes is forbidden. Exiting.")
        sys.exit(1)

    # Filter data
    filtered = [row for row in data if row['ward'] == target_ward and row['category'] == target_category]
    
    # Sort strictly by period (YYYY-MM string sorts chronologically)
    filtered.sort(key=lambda x: x['period'])

    results = []
    
    for i in range(len(filtered)):
        curr_row = filtered[i]
        period = curr_row['period']
        budget = curr_row['budgeted_amount']
        actual = curr_row['actual_spend']
        notes = curr_row['notes']
        
        # ENFORCEMENT 3: Flag NULLs before computing
        if not actual.strip():
            results.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "budgeted_amount": budget,
                "actual_spend": "NULL",
                "growth_metric": "FLAGGED_NULL",
                "notes": notes,
                "formula": "NULL_ENCOUNTERED: NO_COMPUTE"
            })
            continue
            
        # Actual computation logic
        curr_actual = float(actual)
        
        if growth_type == "MoM":
            if i == 0:
                growth = "N/A"
                formula = "No previous month"
            else:
                prev_row = filtered[i-1]
                prev_actual_str = prev_row['actual_spend']
                
                if not prev_actual_str.strip():
                    growth = "N/A"
                    formula = "Previous month was NULL"
                else:
                    prev_actual = float(prev_actual_str)
                    if prev_actual > 0:
                        calc = ((curr_actual - prev_actual) / prev_actual) * 100
                        growth = f"{calc:+.1f}%"
                        formula = f"(({curr_actual} - {prev_actual}) / {prev_actual}) * 100"
                    else:
                        growth = "N/A"
                        formula = "Div/0"
                        
            results.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "budgeted_amount": budget,
                "actual_spend": curr_actual,
                "growth_metric": growth,
                "notes": notes,
                "formula": formula
            })

    # Write output
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_metric", "notes", "formula"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Wrote strict growth output to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False, help="Must specify ward")
    parser.add_argument("--category", required=False, help="Must specify category")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    compute_growth(data, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()
