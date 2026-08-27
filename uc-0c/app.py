"""
UC-0C app.py
Number That Looks Right - Civic Data MoM Processor.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    """
    Reads CSV, validates columns, reports null count and which rows before returning
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_rows_report = []

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames)):
            print(f"Error: Missing required columns. Expected: {required_cols}")
            sys.exit(1)
            
        for idx, row in enumerate(reader, start=1):
            if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                null_rows_report.append(row)
            data.append(row)

    print(f"Dataset successfully loaded. Validated null check: Found {len(null_rows_report)} deliberate null actual_spend rows.")
    for nr in null_rows_report:
        print(f"  - NULL found at: Period: {nr['period']}, Ward: {nr['ward']}, Category: {nr['category']}")

    return data

def compute_growth(dataset, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Enforces rules: no global aggregations, flagged nulls, requires growth_type.
    """
    if not growth_type:
        print("REFUSAL TRIGGERED: --growth-type not specified. I cannot assume a formula (MoM/YoY), please explicitly request the metric type.")
        sys.exit(1)
        
    if not ward or not category or ward == "ALL" or category == "ALL":
        print("REFUSAL TRIGGERED: Cannot aggregate across wards or categories. Execution refused.")
        sys.exit(1)

    # Filter isolated
    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]
    
    if not filtered:
        print(f"No records found filtering against isolation parameters (ward: {ward}, category: {category}).")
        sys.exit(1)

    # Sort sequentially
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_val = None
    
    for row in filtered:
        period = row["period"]
        raw_val = row["actual_spend"]
        notes = row.get("notes", "")

        out_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": raw_val,
            "growth_type": growth_type,
            "growth_metric": "n/a",
            "formula": "n/a",
            "notes": notes,
        }

        if not raw_val or raw_val.strip() == "" or raw_val.upper() == "NULL":
            # Flagging explicitly due to Null actuals
            out_row["growth_metric"] = "FLAGGED NULL"
            out_row["formula"] = "Cannot compute (operand missing)"
            prev_val = None # Next calculation won't be sequential
        else:
            curr_float = float(raw_val)
            if growth_type.upper() == "MOM":
                if prev_val is not None:
                    # Calculate MoM
                    metric = ((curr_float - prev_val) / prev_val) * 100
                    prefix = "+" if metric > 0 else "−" if metric < 0 else ""
                    out_row["growth_metric"] = f"{prefix}{abs(metric):.1f}%"
                    out_row["formula"] = f"(({curr_float} - {prev_val}) / {prev_val}) * 100"
                else:
                    out_row["growth_metric"] = "n/a"
                    out_row["formula"] = "N/A (no prior baseline available)"
                prev_val = curr_float
            else:
                out_row["growth_metric"] = "UNKNOWN GROWTH METRIC"
                out_row["formula"] = f"Unmapped metric '{growth_type}'"
                
        results.append(out_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Computation Agent")
    parser.add_argument("--input", required=True, help="Input CSV subset")
    parser.add_argument("--ward", default=None, help="Specific scoping target Ward")
    parser.add_argument("--category", default=None, help="Specific scoping target Category")
    parser.add_argument("--growth-type", default=None, help="Calculation assumption explicitly mapped")
    parser.add_argument("--output", required=True, help="Destination CSV file name")
    args = parser.parse_args()

    data = load_dataset(args.input)
    computed_records = compute_growth(data, args.ward, args.category, args.growth_type)

    if computed_records:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            headers = ["period", "ward", "category", "actual_spend", "growth_type", "growth_metric", "formula", "notes"]
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(computed_records)
            
        print(f"Exported aggregated compliance growth to -> {args.output}")

if __name__ == "__main__":
    main()
