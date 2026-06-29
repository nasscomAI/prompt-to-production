import argparse
import csv
import os
import sys

def load_dataset(file_path, ward, category):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ward"] == ward and row["category"] == category:
                records.append(row)
                
    # Sort chronologically by the period column (YYYY-MM)
    records.sort(key=lambda x: x["period"])
    return records

def compute_growth(records, growth_type):
    # Enforce Rule 4: Refuse if growth_type is missing or invalid
    if not growth_type or growth_type not in ["MoM"]:
        print("Error: Invalid or missing --growth-type flag. System refuses to guess.")
        sys.exit(1)
        
    output_rows = []
    
    for i, current in enumerate(records):
        period = current["period"]
        current_spend_str = current["actual_spend"].strip()
        notes = current["notes"] if current["notes"] else "No notes provided"
        
        # Enforce Rule 2: Flag every null row before computing
        if not current_spend_str:
            output_rows.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": f"FLAGGED: {notes}",
                "formula": "n/a"
            })
            continue
            
        current_spend = float(current_spend_str)
        
        # For the very first row, there is no previous period to compare against
        if i == 0:
            output_rows.append({
                "period": period,
                "actual_spend": str(current_spend),
                "growth": "n/a",
                "formula": "First period (baseline)"
            })
            continue
            
        prev = records[i - 1]
        prev_spend_str = prev["actual_spend"].strip()
        
        # If the immediate previous row was a null record, we cannot compute MoM growth safely
        if not prev_spend_str:
            output_rows.append({
                "period": period,
                "actual_spend": str(current_spend),
                "growth": "Cannot compute",
                "formula": f"Previous period spend was NULL due to: {prev['notes']}"
            })
            continue
            
        prev_spend = float(prev_spend_str)
        
        if prev_spend == 0:
            growth_val = "n/a"
            formula_str = f"({current_spend} - 0) / 0"
        else:
            diff = current_spend - prev_spend
            pct = (diff / prev_spend) * 100
            sign = "+" if pct >= 0 else ""
            growth_val = f"{sign}{pct:.1f}%"
            # Enforce Rule 3: Show exact formula layout
            formula_str = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            
        output_rows.append({
            "period": period,
            "actual_spend": str(current_spend),
            "growth": growth_val,
            "formula": formula_str
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Tracking Tool")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target expenditure category")
    parser.add_argument("--growth-type", required=True, help="MoM or alternative analytics metrics")
    parser.add_argument("--output", required=True, help="Path to save growth_output.csv")
    args = parser.parse_args()

    # Enforce Rule 1: Refuse global aggregations
    if args.ward.lower() in ["all", "any", "total"] or args.category.lower() in ["all", "any", "total"]:
        print("Error: All-ward or all-category aggregation requests are explicitly prohibited. System refuses to execute.")
        sys.exit(1)

    records = load_dataset(args.input, args.ward, args.category)
    
    if not records:
        print(f"Warning: No matching rows found for Ward: '{args.ward}' and Category: '{args.category}'")
        
    calculated_data = compute_growth(records, args.growth_type)
    
    # Save target analytics values
    fieldnames = ["period", "actual_spend", "growth", "formula"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(calculated_data)
        
    print(f"Done. Processed growth analysis exported cleanly to: {args.output}")

if __name__ == "__main__":
    main()
