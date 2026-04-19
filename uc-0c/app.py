"""
UC-0C app.py — Budget Analyst.
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os

def load_dataset(input_path: str):
    """
    Skill: load_dataset
    Reads CSV and identifies null actual_spend rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    data = []
    null_rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Check for null or blank actual_spend
            if not row.get("actual_spend"):
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "note": row.get("notes", "No reason provided")
                })
            data.append(row)
    
    if null_rows:
        print(f"AUDIT REPORT: Detected {len(null_rows)} missing actual_spend entries.")
        for nr in null_rows:
            print(f"  - [{nr['period']}] {nr['ward']} | {nr['category']}: {nr['note']}")
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Filters data and calculates MoM growth with formula transparency.
    """
    if growth_type.upper() != "MOM":
        raise ValueError(f"Growth type '{growth_type}' is currently not supported or invalid.")

    # Filter for the specific ward and category
    subset = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not subset:
        print(f"Error: No data found for Ward '{ward}' and Category '{category}'.")
        return []

    # Sort by period to ensure MoM is chronological
    subset.sort(key=lambda x: x["period"])

    results = []
    for i in range(len(subset)):
        curr = subset[i]
        prev = subset[i-1] if i > 0 else None
        
        period = curr["period"]
        actual = curr.get("actual_spend")
        
        result_row = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual if actual else "NULL",
            "growth": "n/a",
            "formula": "n/a"
        }

        if not actual:
            result_row["growth"] = "FLAGGED"
            result_row["formula"] = f"CRITICAL: {curr.get('notes', 'Missing data')}"
        elif prev and prev.get("actual_spend"):
            try:
                c_val = float(actual)
                p_val = float(prev["actual_spend"])
                growth = ((c_val - p_val) / p_val) * 100
                result_row["growth"] = f"{growth:+.1f}%"
                result_row["formula"] = f"({c_val} - {p_val}) / {p_val}"
            except (ValueError, ZeroDivisionError):
                result_row["growth"] = "Error"
                result_row["formula"] = "Invalid numerical data"
        elif prev and not prev.get("actual_spend"):
            result_row["growth"] = "n/a"
            result_row["formula"] = "Previous period data missing"
        else:
            result_row["formula"] = "Baseline (First Period)"

        results.append(result_row)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific Ward name")
    parser.add_argument("--category", required=True, help="Specific Category name")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path for growth_output.csv")
    args = parser.parse_args()

    try:
        data = load_dataset(args.input)
        
        print(f"Computing {args.growth_type} for '{args.ward}' | '{args.category}'...")
        results = compute_growth(data, args.ward, args.category, args.growth_type)

        if results:
            keys = results[0].keys()
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Results written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
