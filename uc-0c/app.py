"""
UC-0C — Number That Looks Right
Implementation adhering strictly to RICE -> agents.md -> skills.md rules.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str):
    """Skill: Loads dataset, validates schema, isolates rows."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget CSV not found: {input_path}")

    records = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records

def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list:
    """Skill: Computes growth per period with strict scope and formula enforcement."""
    # Refusal Rule 1: Missing growth type
    if not growth_type:
        print("REFUSAL: Growth type must be specified explicitly (e.g., --growth-type MoM).")
        sys.exit(1)

    # Refusal Rule 2: Cross-ward aggregation request
    if not ward or ward.lower() == "all" or not category or category.lower() == "all":
        print("REFUSAL: Cross-ward or cross-category aggregations are disallowed. Provide specific ward and category.")
        sys.exit(1)

    # Filter records strictly by scope
    filtered = [
        r for r in records 
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    # Sort sequentially by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    prev_actual = None

    for r in filtered:
        period = r["period"]
        actual_raw = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        # Rule: Explicit null handling
        if not actual_raw or actual_raw.upper() == "NULL":
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_percent": "NULL - Not Computed",
                "formula": "N/A (Missing Value)",
                "notes": notes if notes else "Data missing in source"
            })
            prev_actual = None  # Reset baseline due to null break
            continue

        actual_val = float(actual_raw)

        if growth_type.upper() == "MOM":
            if prev_actual is None or prev_actual == 0:
                growth_str = "N/A (First period or preceding month NULL)"
                formula_str = f"MoM Baseline: Current = {actual_val}"
            else:
                growth_pct = ((actual_val - prev_actual) / prev_actual) * 100
                growth_str = f"{growth_pct:+.1f}%"
                formula_str = f"(({actual_val} - {prev_actual}) / {prev_actual}) * 100"

            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_val,
                "growth_percent": growth_str,
                "formula": formula_str,
                "notes": notes
            })
            prev_actual = actual_val
        else:
            print(f"REFUSAL: Unsupported growth type '{growth_type}'. Only MoM is supported.")
            sys.exit(1)

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target Ward name")
    parser.add_argument("--category", required=True, help="Target Category name")
    parser.add_argument("--growth-type", required=True, help="Growth metric type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if results:
        fieldnames = list(results[0].keys())
        with open(args.output, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    print(f"Budget analysis successfully exported to {args.output}")

if __name__ == "__main__":
    main()