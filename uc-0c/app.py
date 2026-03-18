"""
UC-0C app.py — Financial Data Growth Computer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    records = []
    null_rows = []
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2): # +1 for 1-index, +1 for header
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            actual_spend_str = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()
            
            # Explicitly check for deliberate null/blank values
            if actual_spend_str.upper() == "NULL" or not actual_spend_str:
                null_rows.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "notes": notes if notes else "No notes provided"
                })
                actual_spend = None
            else:
                try:
                    actual_spend = float(actual_spend_str)
                except ValueError:
                    actual_spend = None
                    
            records.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "notes": notes
            })
            
    # Flag every null row before computing
    if null_rows:
        print(f"FLAG: Found {len(null_rows)} null actual_spend rows:")
        for nr in null_rows:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} -> Reason: {nr['notes']}")
        print("-" * 50)
            
    return records

def compute_growth(records: list, ward: str, category: str, growth_type: str):
    """
    Takes dataset, ward, category, and growth_type.
    Returns logic-enforced per-period table output rows string.
    """
    if not growth_type:
        return "REFUSAL: --growth-type not specified. Cannot compute growth without explicit parameters."
        
    if not ward or not category:
        return "REFUSAL: System refused to aggregate across wards or categories. Explicit --ward and --category must be provided."
        
    if ward.lower() == "any" or category.lower() == "any":
        return "REFUSAL: System refused to aggregate across wards or categories."

    # Filter to specific isolated ward and category
    filtered = sorted([r for r in records if r["ward"] == ward and r["category"] == category], key=lambda x: x["period"])
    
    if not filtered:
        return "No data found for the specified ward and category."

    output_rows = []
    
    # Calculate MoM
    if growth_type.lower() == "mom":
        for i in range(len(filtered)):
            current = filtered[i]
            cp_spend = current["actual_spend"]
            formula = ""
            growth_str = ""
            
            if cp_spend is None:
                growth_str = "NULL (Flagged: Not computed)"
                formula = "N/A"
            elif i == 0:
                growth_str = "0.0%"
                formula = "Baseline"
            else:
                prev_spend = filtered[i-1]["actual_spend"]
                if prev_spend is None:
                    growth_str = "NULL (Flagged: Previous period null, cannot compute)"
                    formula = "N/A"
                elif prev_spend == 0:
                    growth_str = "Undef"
                    formula = f"( {cp_spend} - 0 ) / 0 * 100"
                else:
                    growth = ((cp_spend - prev_spend) / prev_spend) * 100
                    growth_str = f"{growth:+.1f}%"
                    formula = f"( {cp_spend} - {prev_spend} ) / {prev_spend} * 100"
                    
            output_rows.append({
                "ward": current["ward"],
                "category": current["category"],
                "period": current["period"],
                "actual_spend": current["actual_spend"] if current["actual_spend"] is not None else "NULL",
                "growth": growth_str,
                "formula": formula,
                "notes": current["notes"]
            })
    else:
        return f"REFUSAL: Unrecognized growth-type '{growth_type}'. Cannot guess formula."

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Computer")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=False, help="Ward name (must specify, otherwise Refuse)")
    parser.add_argument("--category", required=False, help="Category name (must specify, otherwise Refuse)")
    parser.add_argument("--growth-type", required=False, help="e.g. MoM (must specify, otherwise Refuse)")
    parser.add_argument("--output", required=True, help="Path to output CSV table")
    args = parser.parse_args()
    
    records = load_dataset(args.input)
    
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified, never guess.")
        sys.exit(1)
        
    result = compute_growth(records, args.ward, args.category, args.growth_type)
    
    if isinstance(result, str) and result.startswith("REFUSAL"):
        print(result)
        sys.exit(1)
    
    if isinstance(result, list):
        fieldnames = ["ward", "category", "period", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result)
        print(f"Successfully computed growth. Filtered results written to {args.output}")

if __name__ == "__main__":
    main()
