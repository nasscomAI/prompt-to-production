import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Loads budget and actual spend data from the CSV file, validating columns
    and identifying/logging any null actual_spend rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    rows = []
    null_rows_count = 0
    null_rows_details = []

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # Validate column names
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no headers.")
        
        missing_cols = [col for col in required_columns if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing_cols)}")
            
        for line_num, row in enumerate(reader, start=2):
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            
            # Try parsing actual_spend
            actual_spend_str = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()
            
            actual_spend = None
            if actual_spend_str != "":
                try:
                    actual_spend = float(actual_spend_str)
                except ValueError:
                    # Treat invalid float as null
                    actual_spend = None
            
            if actual_spend is None:
                null_rows_count += 1
                null_rows_details.append({
                    "line": line_num,
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "notes": notes
                })
                
            budgeted_amount = 0.0
            budgeted_str = row.get("budgeted_amount", "").strip()
            if budgeted_str:
                try:
                    budgeted_amount = float(budgeted_str)
                except ValueError:
                    pass

            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": notes
            })

    print(f"Loaded {len(rows)} rows successfully. Found {null_rows_count} rows with null actual_spend.")
    for details in null_rows_details:
        print(f"  - Line {details['line']}: {details['period']} | {details['ward']} | {details['category']} | Reason: {details['notes']}")
        
    return rows

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates growth in actual spend for a specific ward and category using the
    requested growth type, showing the formula used.
    """
    # Enforcement 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category:
        raise ValueError("Error: Both ward and category must be explicitly specified. General aggregation is refused.")
        
    # Enforcement 4: If growth_type not specified - refuse
    if not growth_type:
        raise ValueError("Error: --growth-type must be explicitly specified (e.g. MoM). Refusing calculation.")
        
    if growth_type != "MoM":
        raise ValueError(f"Error: Unsupported growth type '{growth_type}'. Only 'MoM' is supported.")

    # Filter data for specific ward and category
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not filtered:
        raise ValueError(f"Error: No records found matching ward '{ward}' and category '{category}'.")
        
    # Sort filtered data chronologically by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        curr_spend = row["actual_spend"]
        notes = row["notes"]
        
        growth_str = "NULL"
        formula_str = "N/A"
        
        if curr_spend is None:
            # Enforcement 2: Flag null rows before computing
            growth_str = "NULL"
            formula_str = "N/A"
            notes = notes if notes else "Actual spend is null"
        elif i == 0:
            # First month, no previous month
            growth_str = "NULL"
            formula_str = "N/A"
            notes = "First month in dataset, no previous spend to compare."
        else:
            prev_row = filtered[i - 1]
            prev_spend = prev_row["actual_spend"]
            
            if prev_spend is None:
                growth_str = "NULL"
                formula_str = "N/A"
                notes = "Previous month spend is null, growth cannot be computed."
            else:
                # Compute MoM growth
                diff = curr_spend - prev_spend
                growth_val = diff / prev_spend
                
                # Format formula
                # Show formula used alongside the result (Enforcement 3)
                formula_str = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
                
                # Format growth
                percent = growth_val * 100
                if percent > 0:
                    growth_str = f"+{percent:.1f}%"
                elif percent < 0:
                    growth_str = f"{percent:.1f}%"
                else:
                    growth_str = "0.0%"
                    
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{curr_spend:.1f}" if curr_spend is not None else "NULL",
            "growth": growth_str,
            "formula": formula_str,
            "notes": notes
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g., 'MoM')")
    parser.add_argument("--output", required=True, help="Path to output growth CSV")
    
    args = parser.parse_args()
    
    # Check if growth_type is explicitly specified
    if not args.growth_type:
        print("Refusal Error: --growth-type is not specified. Refusing to guess.", file=sys.stderr)
        sys.exit(1)
        
    try:
        # Step 1: Load dataset
        data = load_dataset(args.input)
        
        # Step 2: Compute growth
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Step 3: Write results
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth calculation complete. Results written to {args.output}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Refusal/Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
