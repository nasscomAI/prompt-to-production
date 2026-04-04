"""
UC-0C app.py — Strict Financial Analyst
"""
import argparse
import csv
import sys
import copy

def load_dataset(filepath: str) -> list:
    """Reads CSV, validates columns, reports nulls, and returns data."""
    data = []
    null_count = 0
    null_details = []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
            for req in required:
                if req not in reader.fieldnames:
                    print(f"Error: Missing critical column '{req}' in {filepath}")
                    sys.exit(1)
                    
            for row in reader:
                data.append(row)
                if not row["actual_spend"].strip():
                    null_count += 1
                    null_details.append(f"{row['period']} · {row['ward']} · {row['category']} (Note: {row['notes']})")
                    
        print(f"Dataset Loaded. Validated {len(data)} rows.")
        if null_count > 0:
            print(f"WARNING: Discovered {null_count} null actual_spend rows specifically:")
            for detail in null_details:
                print(f" - {detail}")
            print("These rows will be explicitly flagged and excluded from rolling computations.")
            
        return data
        
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'")
        sys.exit(1)


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Computes growth only on explicit slices. Explains all formulas and handles nulls safely."""
    
    # Enforcement Rule: Refuse execution without specific parameters
    if not ward or ward.lower() == "any" or ward.lower() == "all":
        print("REFUSED: Never aggregate across wards unless explicitly instructed. Please pass a specific --ward.")
        sys.exit(1)
    if not category or category.lower() == "any" or category.lower() == "all":
        print("REFUSED: Never aggregate across categories unless explicitly instructed. Please pass a specific --category.")
        sys.exit(1)
    if not growth_type:
        print("REFUSED: Growth type not explicitly defined. Never guess.")
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"REFUSED: Currently only MoM is supported. Unknown growth-type: {growth_type}")
        sys.exit(1)

    # Filter data
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    if not filtered:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'")
        return []
        
    # Sort chronologically
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    prev_val = None
    
    for row in filtered:
        output_row = copy.deepcopy(row)
        current_str = row["actual_spend"].strip()
        
        if not current_str:
            output_row["growth"] = "NULL"
            output_row["formula"] = "Must be flagged — not computed"
            # Since this month is null, the *next* month cannot have a proper MoM!
            prev_val = None
        else:
            try:
                curr_val = float(current_str)
                if prev_val is None:
                    # Baseline month or previous month was null
                    output_row["growth"] = "n/a"
                    output_row["formula"] = "Baseline period / No valid previous period"
                else:
                    if prev_val == 0.0:
                        output_row["growth"] = "Infinite"
                        output_row["formula"] = f"({curr_val} / 0) - 1"
                    else:
                        growth = (curr_val / prev_val) - 1
                        sign = "+" if growth > 0 else ""
                        output_row["growth"] = f"{sign}{growth*100:.1f}%"
                        output_row["formula"] = f"({curr_val} / {prev_val}) - 1"
                
                prev_val = curr_val
            except ValueError:
                output_row["growth"] = "ERROR"
                output_row["formula"] = "Invalid numeric data"
                prev_val = None
                
        results.append(output_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific Ward name")
    parser.add_argument("--category", required=False, help="Specific Category name")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output.csv")
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes", "growth", "formula"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Per-ward per-category table written to {args.output}")

if __name__ == "__main__":
    main()
