"""
UC-0C app.py — Budget Growth Analysis App
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def load_dataset(filepath: str):
    """
    Skill: load_dataset
    Reads CSV, validates headers, reports null count and null rows.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Budget dataset file not found at: {filepath}")

    rows = []
    null_rows = []
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.upper() == "NULL":
                row["actual_spend_val"] = None
                null_rows.append((idx, row))
            else:
                try:
                    row["actual_spend_val"] = float(raw_spend)
                except ValueError:
                    row["actual_spend_val"] = None
                    null_rows.append((idx, row))
            rows.append(row)

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: compute_growth
    Filters dataset by ward and category, computes period growth (MoM/YoY),
    shows formula used, and flags null spend rows.
    """
    if not growth_type:
        print("ERROR/REFUSAL: --growth-type was not specified. System refuses to guess between MoM and YoY.", file=sys.stderr)
        sys.exit(1)

    if not ward or ward.lower() in ["all", "any", "total"]:
        print("ERROR/REFUSAL: Aggregation across all wards is prohibited by RICE enforcement rules.", file=sys.stderr)
        sys.exit(1)

    if not category or category.lower() in ["all", "any", "total"]:
        print("ERROR/REFUSAL: Aggregation across all categories is prohibited by RICE enforcement rules.", file=sys.stderr)
        sys.exit(1)

    # Filter dataset
    filtered = [r for r in rows if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_val = None

    for r in filtered:
        period = r["period"]
        b_amount = r["budgeted_amount"]
        a_val = r["actual_spend_val"]
        notes = r.get("notes", "").strip()

        if a_val is None:
            growth_str = "NULL (Flagged)"
            formula_str = "N/A - Missing actual_spend"
            flag_str = f"NULL_DATA: {notes}" if notes else "NULL_DATA"
            actual_str = "NULL"
        else:
            actual_str = f"{a_val:.1f}"
            if prev_val is None:
                growth_str = "N/A (Baseline)"
                formula_str = "Baseline period - no prior period data"
                flag_str = ""
            else:
                if growth_type.upper() == "MOM":
                    diff = a_val - prev_val
                    rate = (diff / prev_val) * 100.0
                    growth_str = f"{rate:+.1f}%"
                    formula_str = f"((Actual[{period}] {a_val:.1f} - Actual[Prev] {prev_val:.1f}) / {prev_val:.1f}) * 100"
                    flag_str = ""
                else:
                    growth_str = "N/A"
                    formula_str = f"Unsupported growth-type {growth_type}"
                    flag_str = "UNSUPPORTED_GROWTH_TYPE"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": b_amount,
            "actual_spend": actual_str,
            "growth": growth_str,
            "formula": formula_str,
            "notes": notes,
            "flag": flag_str
        })

        # Update previous value only if current value is valid
        if a_val is not None:
            prev_val = a_val

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis App")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes", "flag"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth analysis written to {args.output}")


if __name__ == "__main__":
    main()
