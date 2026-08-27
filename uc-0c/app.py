"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    data = []
    null_count = 0
    with open(input_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Check required columns
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(reader.fieldnames):
            raise ValueError(f"CSV missing required columns: {required_cols - set(reader.fieldnames)}")
            
        for row in reader:
            # Parse numbers, track nulls
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.upper() == "NULL":
                row["actual_spend"] = None
                null_count += 1
            else:
                try:
                    row["actual_spend"] = float(raw_spend)
                except ValueError:
                    row["actual_spend"] = None
                    null_count += 1
                    
            try:
                row["budgeted_amount"] = float(row.get("budgeted_amount", 0))
            except ValueError:
                row["budgeted_amount"] = 0.0
                
            data.append(row)
            
    print(f"Loaded {len(data)} rows. Found {null_count} null actual_spend rows.")
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters data by ward and category, and calculates MoM/YoY growth.
    """
    # Sort data by period to ensure chronologically correct MoM calculations
    # Periods are in YYYY-MM format, so alphabetical sort works correctly
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])
    
    if not filtered:
        print(f"No records found for ward='{ward}' and category='{category}'")
        return []
        
    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row.get("notes", "").strip()
        
        growth = "n/a"
        formula = "n/a"
        
        if actual_spend is None:
            # Null row
            growth = "NULL"
            formula = "n/a"
            reason = notes if notes else "Actual spend is null"
        else:
            reason = notes
            
            if growth_type.upper() == "MOM":
                if i == 0:
                    growth = "n/a"
                    formula = "No previous month data"
                else:
                    prev_row = filtered[i-1]
                    prev_spend = prev_row["actual_spend"]
                    if prev_spend is None:
                        growth = "NULL"
                        formula = f"(({actual_spend:.1f} - NULL) / NULL) * 100"
                        reason = "Previous month's actual spend is null"
                    else:
                        diff = actual_spend - prev_spend
                        growth_val = (diff / prev_spend) * 100
                        growth = f"{growth_val:+.1f}%"
                        formula = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
            elif growth_type.upper() == "YOY":
                # Find the same month of the previous year
                curr_year, curr_month = period.split("-")
                prev_year = str(int(curr_year) - 1)
                prev_period = f"{prev_year}-{curr_month}"
                
                prev_row = next((r for r in filtered if r["period"] == prev_period), None)
                if not prev_row:
                    growth = "n/a"
                    formula = f"No data for previous year period {prev_period}"
                else:
                    prev_spend = prev_row["actual_spend"]
                    if prev_spend is None:
                        growth = "NULL"
                        formula = f"(({actual_spend:.1f} - NULL) / NULL) * 100"
                        reason = f"Previous year's actual spend ({prev_period}) is null"
                    else:
                        diff = actual_spend - prev_spend
                        growth_val = (diff / prev_spend) * 100
                        growth = f"{growth_val:+.1f}%"
                        formula = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
            else:
                raise ValueError(f"Unsupported growth type: {growth_type}")
                
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "NULL" if actual_spend is None else f"{actual_spend:.1f}",
            "growth": growth,
            "formula": formula,
            "notes": reason
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output growth_output.csv")
    args = parser.parse_args()
    
    # 1. Enforce refusal rule for missing growth-type
    if not args.growth_type:
        print("Error: Growth type (--growth-type) must be specified. Please choose MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    # 2. Enforce refusal rules for aggregation (missing or 'All' or 'Any' for ward/category)
    if not args.ward or args.ward.strip().lower() in ["all", "any", "aggregated", "total"]:
        print("Refusal Error: This system refuses to aggregate across multiple wards. You must specify a single, specific ward.", file=sys.stderr)
        sys.exit(1)
        
    if not args.category or args.category.strip().lower() in ["all", "any", "aggregated", "total"]:
        print("Refusal Error: This system refuses to aggregate across multiple categories. You must specify a single, specific category.", file=sys.stderr)
        sys.exit(1)
        
    # 3. Load dataset
    try:
        data = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 4. Compute growth
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"Error computing growth: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 5. Write output
    if results:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Growth output written to {args.output}")
    else:
        print("No output written because no records matched the filters.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
