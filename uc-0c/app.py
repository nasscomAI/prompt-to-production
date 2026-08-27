import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Reads the CSV data, validates the schema, and reports the total count
    and exact locations of any null values before returning the dataset.
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    dataset = []
    null_report = []
    
    if not os.path.exists(filepath):
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate schema
            if not reader.fieldnames:
                print("Error: CSV is empty or missing headers.")
                sys.exit(1)
                
            for col in required_columns:
                if col not in reader.fieldnames:
                    print(f"Error: Missing expected column: {col}")
                    sys.exit(1)
            
            for i, row in enumerate(reader, start=2): # line 1 is header
                actual_spend_raw = row.get("actual_spend", "").strip()
                if actual_spend_raw == "" or actual_spend_raw.lower() == "null" or actual_spend_raw.lower() == "none":
                    row["actual_spend"] = None
                    null_report.append({
                        "row_num": i,
                        "period": row.get("period"),
                        "ward": row.get("ward"),
                        "category": row.get("category"),
                        "reason": row.get("notes")
                    })
                else:
                    try:
                        row["actual_spend"] = float(actual_spend_raw)
                    except ValueError:
                        print(f"Error: Invalid actual_spend value at row {i}: {actual_spend_raw}")
                        sys.exit(1)
                
                dataset.append(row)
                
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
    
    # Report nulls
    print(f"--- Data Load Report ---")
    print(f"Total rows loaded: {len(dataset)}")
    print(f"Total null actual_spend values found: {len(null_report)}")
    for null_row in null_report:
        print(f"  - Row {null_row['row_num']} ({null_row['period']}): Ward '{null_row['ward']}', Category '{null_row['category']}' - Reason: {null_row['reason']}")
    print(f"------------------------\n")
    
    return {
        "data": dataset,
        "null_report": null_report
    }

def compute_growth(dataset, ward, category, growth_type):
    """
    Computes the requested growth metric for a specific ward and category over time,
    outputting a period-by-period table with explicit formulas.
    """
    if not growth_type:
        print("Error: --growth-type must be specified. I cannot guess the default. Refusing to proceed.")
        sys.exit(1)
        
    if not ward or not category or ward.lower() in ("all", "any") or category.lower() in ("all", "any"):
        print("Error: Refusing to aggregate across multiple wards or categories. Please specify exactly one ward and one category.")
        sys.exit(1)
        
    # Filter dataset
    filtered_data = []
    for row in dataset:
        if row["ward"] == ward and row["category"] == category:
            filtered_data.append(row)
            
    # Sort by period (assuming YYYY-MM)
    filtered_data.sort(key=lambda x: x["period"])
    
    if not filtered_data:
        print(f"Warning: No data found for Ward '{ward}' and Category '{category}'.")
    
    output_rows = []
    
    for i, row in enumerate(filtered_data):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        
        out_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": actual_spend if actual_spend is not None else "NULL",
            "Growth Type": growth_type,
            "Calculated Growth": None,
            "Formula Used": None,
            "Flag Reason": None
        }
        
        if actual_spend is None:
            out_row["Calculated Growth"] = "Not Computed"
            out_row["Formula Used"] = "N/A (Null Value)"
            out_row["Flag Reason"] = f"Null spend flagged. Reason: {notes}"
        else:
            if growth_type.lower() == "mom":
                if i == 0:
                    out_row["Calculated Growth"] = "N/A"
                    out_row["Formula Used"] = "No previous month"
                else:
                    prev_row = filtered_data[i-1]
                    prev_spend = prev_row["actual_spend"]
                    if prev_spend is None:
                        out_row["Calculated Growth"] = "Not Computed"
                        out_row["Formula Used"] = "Previous month was null"
                        out_row["Flag Reason"] = "Cannot compute MoM due to previous null"
                    elif prev_spend == 0:
                        out_row["Calculated Growth"] = "N/A"
                        out_row["Formula Used"] = f"({actual_spend} - 0) / 0"
                        out_row["Flag Reason"] = "Cannot divide by zero"
                    else:
                        growth = (actual_spend - prev_spend) / prev_spend * 100
                        out_row["Calculated Growth"] = f"{growth:+.1f}%"
                        out_row["Formula Used"] = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
            elif growth_type.lower() == "yoy":
                # Assuming YoY means comparing to same month last year.
                year, month = period.split("-")
                prev_year_period = f"{int(year)-1}-{month}"
                
                prev_row = next((r for r in filtered_data if r["period"] == prev_year_period), None)
                
                if not prev_row:
                    out_row["Calculated Growth"] = "N/A"
                    out_row["Formula Used"] = "No previous year same month"
                else:
                    prev_spend = prev_row["actual_spend"]
                    if prev_spend is None:
                        out_row["Calculated Growth"] = "Not Computed"
                        out_row["Formula Used"] = "Previous year same month was null"
                        out_row["Flag Reason"] = "Cannot compute YoY due to previous null"
                    elif prev_spend == 0:
                        out_row["Calculated Growth"] = "N/A"
                        out_row["Formula Used"] = f"({actual_spend} - 0) / 0"
                        out_row["Flag Reason"] = "Cannot divide by zero"
                    else:
                        growth = (actual_spend - prev_spend) / prev_spend * 100
                        out_row["Calculated Growth"] = f"{growth:+.1f}%"
                        out_row["Formula Used"] = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
            else:
                print(f"Error: Unsupported growth type '{growth_type}'. Only 'MoM' and 'YoY' are supported.")
                sys.exit(1)
                
        output_rows.append(out_row)
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Analysis Agent")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=False, help="Ward name (must be exact)")
    parser.add_argument("--category", required=False, help="Category name (must be exact)")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type must be specified. I cannot guess the default. Refusing to proceed.")
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("Error: --ward and --category must be explicitly specified to prevent unauthorized aggregation. Refusing to proceed.")
        sys.exit(1)

    dataset_info = load_dataset(args.input)
    
    growth_results = compute_growth(
        dataset=dataset_info["data"],
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )
    
    # Write output
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend", "Growth Type", "Calculated Growth", "Formula Used", "Flag Reason"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in growth_results:
            writer.writerow(row)
            
    print(f"Success: Wrote {len(growth_results)} rows to {args.output}")

if __name__ == "__main__":
    main()
