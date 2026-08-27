"""
UC-0C app.py — Number That Looks Right
Starter file. Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    data = []
    null_rows = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Standardize headers in case of BOM or case issues
            headers = [h.strip().lower() for h in reader.fieldnames]
            reader.fieldnames = headers
            
            for i, row in enumerate(reader):
                val = row.get("actual_spend", "").strip()
                if not val:
                    null_rows.append({"index": i+2, "ward": row.get("ward", ""), "category": row.get("category", ""), "period": row.get("period", ""), "notes": row.get("notes", "")})
                data.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f">>> VALIDATION: Loaded dataset with {len(null_rows)} explicitly flagged NULL 'actual_spend' rows.")
        for nr in null_rows:
            print(f"    - Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Notes: {nr['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not ward or ward.lower() == "any" or not category or category.lower() == "any":
        print("REFUSED: Wrong Aggregation Level. All-ward/All-category aggregation is strictly prohibited. You must specify an exact ward and category.")
        sys.exit(1)
        
    # Enforcement Rule 4: If `--growth-type` not specified — refuse and ask, never guess
    if not growth_type:
        print("REFUSED: Formula Assumption. '--growth-type' was not specified. I cannot compute without knowing the exact aggregation formula (e.g., MoM or YoY).")
        sys.exit(1)
        
    filtered = sorted([d for d in data if d.get("ward", "") == ward and d.get("category", "") == category], key=lambda x: x.get("period", ""))
    
    results = []
    for i, row in enumerate(filtered):
        period = row.get("period", "")
        actual_spend = row.get("actual_spend", "").strip()
        notes = row.get("notes", "")
        
        result_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual_spend,
            f"{growth_type} Growth": "n/a",
            "Formula Used": "n/a",
            "Null Flag Details": ""
        }
        
        # Enforcement Rule 2: Flag every null row before computing — report null reason from the notes column
        if not actual_spend:
            result_row["Actual Spend (₹ lakh)"] = "NULL"
            result_row[f"{growth_type} Growth"] = "Must be flagged — not computed"
            result_row["Null Flag Details"] = notes
            result_row["Formula Used"] = "Skipped due to NULL actual_spend"
        else:
            if growth_type == "MoM":
                # Compute Month-over-Month
                if i == 0:
                    result_row[f"{growth_type} Growth"] = "n/a"
                    result_row["Formula Used"] = "N/A (First month recorded)"
                else:
                    prev_spend_str = filtered[i-1].get("actual_spend", "").strip()
                    if not prev_spend_str:
                        result_row[f"{growth_type} Growth"] = "Cannot compute"
                        result_row["Null Flag Details"] = f"Previous month ({filtered[i-1].get('period', '')}) was NULL"
                        result_row["Formula Used"] = "actual_spend_current / NULL - 1"
                    else:
                        current = float(actual_spend)
                        prev = float(prev_spend_str)
                        if prev == 0:
                            growth = float('inf')
                        else:
                            growth = ((current - prev) / prev) * 100
                        sign = "+" if growth > 0 else ""
                        result_row[f"{growth_type} Growth"] = f"{sign}{growth:.1f}%"
                        # Enforcement Rule 3: Show formula used in every output row alongside the result
                        result_row["Formula Used"] = f"(({current} - {prev}) / {prev}) * 100"
            else:
                result_row[f"{growth_type} Growth"] = "Unsupported growth type"
                result_row["Formula Used"] = "Unknown"
                
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Aggregator")
    parser.add_argument("--input", required=True, help="Input CSV file")
    # Setting these arguments to not required natively, so that we can intercept and throw exact refusal messages cleanly.
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        fieldnames = results[0].keys()
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f">>> OUTPUT: Done. Detailed per-period actuals, explicit null flags, and math formulas written to '{args.output}'.")
        except Exception as e:
            print(f"Error writing to {args.output}: {e}")
            sys.exit(1)
    else:
        print(">>> WARNING: No dataset rows matched the specified ward and category.")

if __name__ == "__main__":
    main()
