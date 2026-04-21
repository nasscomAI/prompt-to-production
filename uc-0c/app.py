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
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers or not all(col in headers for col in required_columns):
                raise ValueError(f"Missing required columns. Expected: {required_columns}")
            
            for row in reader:
                data.append(row)
                actual_spend = row.get("actual_spend", "").strip()
                if not actual_spend or actual_spend.lower() == "null":
                    null_rows.append(row)
                    
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f"FLAGGED: Found {len(null_rows)} rows with null actual_spend.")
        for row in null_rows:
            print(f"  - {row['period']} · {row['ward']} · {row['category']}: {row['notes']}")
            
    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    # Filter data to only the specific ward and category
    filtered_data = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    # Sort chronologically
    filtered_data.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered_data)):
        current_row = filtered_data[i]
        period = current_row["period"]
        actual_spend_str = current_row.get("actual_spend", "").strip()
        
        if not actual_spend_str or actual_spend_str.lower() == "null":
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend": "NULL",
                "MoM Growth": "Must be flagged — not computed",
                "Formula Used": "N/A - Null value detected"
            })
            continue
            
        current_spend = float(actual_spend_str)
        
        if growth_type.lower() == "mom":
            if i == 0:
                results.append({
                    "Ward": ward,
                    "Category": category,
                    "Period": period,
                    "Actual Spend": current_spend,
                    "MoM Growth": "N/A (First period)",
                    "Formula Used": "N/A"
                })
            else:
                prev_row = filtered_data[i-1]
                prev_spend_str = prev_row.get("actual_spend", "").strip()
                if not prev_spend_str or prev_spend_str.lower() == "null":
                    results.append({
                        "Ward": ward,
                        "Category": category,
                        "Period": period,
                        "Actual Spend": current_spend,
                        "MoM Growth": "N/A (Previous period is NULL)",
                        "Formula Used": "N/A - Previous value missing"
                    })
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth_pct = "N/A (Div by zero)"
                        formula = f"({current_spend} - {prev_spend}) / {prev_spend}"
                    else:
                        growth_val = (current_spend - prev_spend) / prev_spend * 100
                        growth_pct = f"{growth_val:+.1f}%"
                        formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                        
                    results.append({
                        "Ward": ward,
                        "Category": category,
                        "Period": period,
                        "Actual Spend": current_spend,
                        "MoM Growth": growth_pct,
                        "Formula Used": formula
                    })
        else:
            print(f"REFUSED: Unknown growth-type '{growth_type}'. Only MoM is fully supported in this script.")
            sys.exit(1)
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator Agent")
    parser.add_argument("--input", required=True, help="Path to input budget csv file")
    parser.add_argument("--ward", required=False, help="Specific ward to calculate for")
    parser.add_argument("--category", required=False, help="Specific category to calculate for")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write the output csv file")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: Refuse if --growth-type not specified
    if not args.growth_type:
        print("REFUSED: --growth-type not specified. Please provide it, I will not guess.")
        sys.exit(1)
        
    # Enforcement Rule 1: Refuse if asked to aggregate (or if ward/category missing)
    if not args.ward or args.ward.lower() == "all" or not args.category or args.category.lower() == "all":
        print("REFUSED: Never aggregate across wards or categories unless explicitly instructed.")
        sys.exit(1)

    print("Loading dataset...")
    dataset, nulls = load_dataset(args.input)
    
    print("Computing growth...")
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    print("Writing output...")
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not results:
                print("No results to write.")
                sys.exit(0)
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Output successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
