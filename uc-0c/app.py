"""
UC-0C app.py — Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Read CSV, validate columns, and return data.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV is missing required columns. Required: {required_cols}")
        
        for row in reader:
            data.append(row)
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM or YoY growth for a specific ward and category.
    """
    # Refusal validation rules
    if not ward or ward.lower() in ["all", "any", "total", "aggregate"]:
        raise ValueError("Error: All-ward aggregation is not permitted. You must specify a single ward.")
        
    if not category or category.lower() in ["all", "any", "total", "aggregate"]:
        raise ValueError("Error: All-category aggregation is not permitted. You must specify a single category.")
        
    if not growth_type:
        raise ValueError("Error: --growth-type is not specified. Refusing to guess. Please specify MoM or YoY.")
        
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Error: Unsupported growth-type '{growth_type}'. Supported: MoM, YoY.")

    # Filter rows matching the ward and category
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    
    if not filtered:
        raise ValueError(f"No records found matching ward '{ward}' and category '{category}'.")
        
    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda r: r["period"])
    
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        # Check if actual spend is null/blank
        if not actual_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula_or_note": f"FLAGGED: Actual spend is null. Note: {notes}"
            })
            continue
            
        actual_val = float(actual_str)
        
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_val,
                    "growth": "N/A",
                    "formula_or_note": "First period in dataset (no baseline)"
                })
            else:
                prev_row = filtered[i-1]
                prev_actual_str = prev_row["actual_spend"].strip()
                if not prev_actual_str:
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": actual_val,
                        "growth": "NULL",
                        "formula_or_note": f"FLAGGED: Previous month ({prev_row['period']}) actual spend is null."
                    })
                else:
                    prev_val = float(prev_actual_str)
                    if prev_val == 0:
                        results.append({
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "actual_spend": actual_val,
                            "growth": "N/A",
                            "formula_or_note": "Cannot compute MoM growth: previous actual spend is 0."
                        })
                    else:
                        diff = actual_val - prev_val
                        rate = (diff / prev_val) * 100
                        sign = "+" if rate >= 0 else ""
                        rate_str = f"{sign}{rate:.1f}%"
                        formula = f"({actual_val} - {prev_val}) / {prev_val} * 100"
                        results.append({
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "actual_spend": actual_val,
                            "growth": rate_str,
                            "formula_or_note": formula
                        })
                        
        elif growth_type == "YoY":
            # For YoY in 2024-xx, we need 2023-xx which is not present in 12-month single-year dataset
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_val,
                "growth": "NULL",
                "formula_or_note": "FLAGGED: Cannot compute YoY growth due to lack of historical baseline data."
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific budget category")
    parser.add_argument("--growth-type", help="MoM or YoY (do not guess if missing)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write output CSV
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula_or_note"]
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth calculation successfully written to {args.output}")
        
    except ValueError as ve:
        print(f"Refusal Error: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
