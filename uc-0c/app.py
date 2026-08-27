"""
UC-0C app.py — Rule-based extractor simulating an ideal CRAFT AI.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list[dict]:
    """Reads CSV, validates columns, reports null count and which rows."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        sys.exit(1)

    null_rows = []
    for row in data:
        if not row.get("actual_spend") or row["actual_spend"].strip() == "":
            null_rows.append(row)

    print(f"Dataset successfully loaded. Identified {len(null_rows)} deliberate null actual_spend values.")
    for r in null_rows:
        print(f"  - Null mapped at {r['period']} · {r['ward']} · {r['category']} (Reason: {r['notes']})")

    return data

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    
    if ward.lower() == "any" or category.lower() == "any":
        print("\n[REFUSAL] Enforcement Rule 1: Cannot aggregate across wards or categories unless explicitly instructed.")
        sys.exit(1)

    if growth_type.lower() not in ["mom", "yoy"]:
        print("\n[REFUSAL] Enforcement Rule 4: Please specify a valid growth-type. Assumed types are strictly forbidden.")
        sys.exit(1)

    # Filter data targeting exact match for atomic dimensions
    filtered_data = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not filtered_data:
        print(f"[ERROR] No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    # Sort strictly by period (YYYY-MM string sorts correctly lexically)
    filtered_data = sorted(filtered_data, key=lambda x: x["period"])
    
    results = []
    prev_val = None

    for row in filtered_data:
        curr_spend_str = row.get("actual_spend", "").strip()
        
        result_row = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": row["actual_spend"],
            "growth": "",
            "formula": "",
            "notes": row["notes"]
        }

        # Handle nulls strictly without assuming zero
        if not curr_spend_str:
            result_row["growth"] = "NULL_SPEND"
            result_row["formula"] = f"Computation bypassed due to missing actual_spend. Reported reason: {row['notes']}"
            results.append(result_row)
            prev_val = None  # Resets calculations that need the prior valid string
            continue
            
        try:
            curr_val = float(curr_spend_str)
        except ValueError:
            # Fails gracefully on bad formatting
            curr_val = None

        if prev_val is not None and curr_val is not None:
             if prev_val == 0:
                 growth_pct = 0.0
             else:
                 growth_pct = ((curr_val - prev_val) / prev_val) * 100
             
             # Standardizing display of results to exactly match the reference
             sign = "+" if growth_pct > 0 else ("-" if growth_pct < 0 else "")
             val = abs(growth_pct)
             result_row["growth"] = f"{sign}{val:.1f}%"
             result_row["formula"] = f"({curr_val} - {prev_val}) / {prev_val} * 100"
        else:
             # First month has no previous month to compare to, or previous month was functionally missing
             result_row["growth"] = "n/a"
             result_row["formula"] = "Insufficient historical data for MoM comparison"
             
        results.append(result_row)
        prev_val = curr_val

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Processing")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv test file")
    parser.add_argument("--ward", required=True, help="Specific ward to extract")
    parser.add_argument("--category", required=True, help="Specific category to calculate against")
    parser.add_argument("--growth-type", required=True, help="Explicit formula type mapping (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    # Notice how we enforce passing argument explicitly through `required=True`. 
    # If the user omits `--growth-type` from the command, python inherently throws an error 
    # and halts without guessing, perfectly matching Enforcement Rule 4.

    args = parser.parse_args()

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    if not results:
        print("Empty table returned.")
        return

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes"]
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nSuccess. Wrote dimension-constrained data to {args.output}")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")

if __name__ == "__main__":
    main()
