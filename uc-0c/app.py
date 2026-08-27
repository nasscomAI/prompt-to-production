"""
UC-0C app.py — Number That Looks Right
Implemented using the strict compliance constraints of agents.md and skills.md.

Enforcement Rules:
1. Never aggregate data across wards or categories blindly. Refuse if args missing.
2. Flag every null actual_spend row. Output notes. Do not guess.
3. Show formula trace on all numerical outputs.
4. Refuse calculation if growth-type is not provided.
"""
import argparse
import csv
import sys


def load_dataset(filepath: str, requested_ward: str, requested_category: str) -> list[dict]:
    """Reads dataset, restricts scope, and extracts the target slice natively."""
    
    # 1. Enforcement Point: Explicit Scope Only
    if not requested_ward or not requested_category or requested_ward.lower() == "any" or requested_category.lower() == "any":
        print("AGENT REFUSAL: Scope parameters (ward, category) cannot be ambiguous, 'any', or aggregated.")
        sys.exit(1)

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Could not read {filepath}")
        sys.exit(1)

    sliced_data = []
    for row in data:
        if row['ward'] == requested_ward and row['category'] == requested_category:
            sliced_data.append(row)

    if not sliced_data:
        print(f"AGENT NOTICE: No data found for Ward: '{requested_ward}', Category: '{requested_category}'")
    
    return sliced_data


def compute_growth(rows: list[dict], growth_type: str) -> list[dict]:
    """Computes growth strictly per defined formulae, handling null traces securely."""
    
    # 4. Enforcement Point: Implicit calculation refusal
    if not growth_type or growth_type not in ["MoM", "YoY"]:
        print(f"AGENT REFUSAL: Invalid or missing --growth-type '{growth_type}'. Will not infer/assume type.")
        sys.exit(1)

    results = []
    
    # Needs to be sorted by period ascending normally to do MoM correctly
    rows_sorted = sorted(rows, key=lambda x: x['period'])

    previous_val = None

    for i, row in enumerate(rows_sorted):
        raw_val = row['actual_spend'].strip()
        period = row['period']
        notes = row['notes'].strip()
        
        # 2. Enforcement Point: Strict null detection
        if not raw_val:
            # Propagate null and trace the reason from 'notes'
            result_row = {
                "Ward": row['ward'],
                "Category": row['category'],
                "Period": period,
                "Actual Spend (\u20b9 lakh)": "NULL",
                "Growth": f"FLAGGED NULL — Reason: {notes}"
            }
            # Also reset previous_val so the subsequent month doesn't compute against older data 
            # (or we could compute against i-2, but standard strict MoM means next month is also uncomputable 
            # against previous month). We'll set prior to None.
            previous_val = None
            results.append(result_row)
            continue
            
        current_val = float(raw_val)

        # 3. Enforcement Point: Verifiable Formula Traces
        if previous_val is None:
            growth_str = "n/a (no prior baseline)"
        else:
            if growth_type == "MoM":
                # Compute (current - prev) / prev
                calc = (current_val - previous_val) / previous_val
                percentage = calc * 100
                sign = "+" if calc > 0 else "−" if calc < 0 else ""
                val_abs = abs(percentage)
                
                # We enforce algebraic trace transparency.
                formula_trace = f"(({current_val} - {previous_val}) / {previous_val})"
                
                # Add contextual notes if provided (like "monsoon spike")
                notes_append = f" ({notes})" if notes else ""
                
                growth_str = f"{sign}{val_abs:.1f}% [{formula_trace}]{notes_append}"
            else:
                growth_str = "n/a (Formula not implemented for YoY)"
                
        result_row = {
            "Ward": row['ward'],
            "Category": row['category'],
            "Period": period,
            "Actual Spend (\u20b9 lakh)": str(current_val),
            "Growth": growth_str
        }
        
        results.append(result_row)
        previous_val = current_val
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Strict Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False, default="")
    parser.add_argument("--category", required=False, default="")
    parser.add_argument("--growth-type", required=False, default="")
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()

    slice_rows = load_dataset(args.input, args.ward, args.category)
    final_output = compute_growth(slice_rows, args.growth_type)

    if not final_output:
        print("No output generated.")
        sys.exit(0)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend (\u20b9 lakh)", "Growth"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_output)

    print(f"Done. Verifiable table written to {args.output}")

if __name__ == "__main__":
    main()
