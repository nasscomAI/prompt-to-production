import argparse
import csv
import sys

def load_dataset(file_path):
    """Reads the CSV dataset, validates columns, and reports the null count and specific rows with nulls before returning the data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            if not columns:
                print("Error: Empty file or no columns found.")
                sys.exit(1)
            
            expected_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not expected_columns.issubset(set(columns)):
                print(f"Error: Missing expected columns. Found: {columns}")
                sys.exit(1)
            
            data = list(reader)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

    null_rows = []
    for row in data:
        spend = row.get("actual_spend", "").strip()
        if not spend or spend.lower() == "null":
            null_rows.append(row)
    
    print(f"Dataset loaded. Total rows: {len(data)}")
    print(f"Null actual_spend count: {len(null_rows)}")
    if null_rows:
        print("Flagged null rows before computation:")
        for r in null_rows:
            note = r.get("notes", "No note provided")
            print(f"  - {r['period']} · {r['ward']} · {r['category']} -> NULL (Reason: {note})")
    
    return data, null_rows

def compute_growth(data, ward, category, growth_type):
    """Computes the specified growth metric for a single ward and category over time, appending the exact formula used to each output row."""
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a growth type (e.g., MoM).")
        sys.exit(1)
        
    if not ward or not category or ward.lower() in ("all", "any") or category.lower() in ("all", "any"):
        print("Error: Aggregation across wards or categories is not allowed. Please specify a single ward and category.")
        sys.exit(1)

    filtered_data = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
    
    filtered_data.sort(key=lambda x: x["period"])
    
    output_rows = []
    
    for i, row in enumerate(filtered_data):
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip()
        note = row.get("notes", "").strip()
        
        out_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": actual_spend_str if actual_spend_str and actual_spend_str.lower() != "null" else "NULL",
            f"{growth_type} Growth": "",
            "Formula": "",
            "Notes": note
        }

        if out_row["Actual Spend"] == "NULL":
            out_row[f"{growth_type} Growth"] = "NULL (Flagged)"
            out_row["Formula"] = "N/A"
            output_rows.append(out_row)
            continue
            
        current_spend = float(actual_spend_str)
        
        if growth_type.lower() == "mom":
            if i > 0:
                prev_spend_str = filtered_data[i-1]["actual_spend"].strip()
                if not prev_spend_str or prev_spend_str.lower() == "null":
                    out_row[f"{growth_type} Growth"] = "Cannot compute (previous month is NULL)"
                    out_row["Formula"] = "N/A"
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        out_row[f"{growth_type} Growth"] = "Undefined"
                        out_row["Formula"] = f"({current_spend} - 0) / 0"
                    else:
                        growth = (current_spend - prev_spend) / prev_spend
                        out_row[f"{growth_type} Growth"] = f"{growth * 100:+.1f}%"
                        out_row["Formula"] = f"({current_spend} - {prev_spend}) / {prev_spend}"
            else:
                out_row[f"{growth_type} Growth"] = "N/A (first period)"
                out_row["Formula"] = "N/A"
        elif growth_type.lower() == "yoy":
            out_row[f"{growth_type} Growth"] = "Cannot compute (no previous year)"
            out_row["Formula"] = "N/A"
        else:
            print(f"Error: Unsupported growth type '{growth_type}'")
            sys.exit(1)
            
        output_rows.append(out_row)
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analysis Agent")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Growth type to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please provide a growth type (e.g., MoM).")
        sys.exit(1)
        
    if not args.ward or not args.category or args.ward.lower() in ("all", "any") or args.category.lower() in ("all", "any"):
        print("Error: Aggregation across wards or categories is not allowed. Please specify a single ward and category.")
        sys.exit(1)
        
    data, null_rows = load_dataset(args.input)
    
    output_rows = compute_growth(data, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not output_rows:
                print("Warning: No data to write.")
                return
                
            writer = csv.DictWriter(f, fieldnames=output_rows[0].keys())
            writer.writeheader()
            writer.writerows(output_rows)
            print(f"Output written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
