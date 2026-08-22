"""
UC-0C — Number That Looks Right
Implementation guided by RICE (agents.md) and skills (skills.md).
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """Read budget CSV dataset and detect null actual_spend rows."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Budget dataset not found: {input_path}")
    
    rows = []
    null_count = 0
    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            period = r.get("period", "").strip()
            ward = r.get("ward", "").strip()
            category = r.get("category", "").strip()
            budgeted_str = r.get("budgeted_amount", "").strip()
            actual_str = r.get("actual_spend", "").strip()
            notes = r.get("notes", "").strip()

            budgeted = float(budgeted_str) if budgeted_str else 0.0
            if actual_str != "" and actual_str.lower() != "null":
                actual = float(actual_str)
                is_null = False
            else:
                actual = None
                is_null = True
                null_count += 1

            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "is_null": is_null,
                "notes": notes,
            })

    print(f"[Info] Loaded {len(rows)} records. Found {null_count} null actual_spend rows.")
    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculate Month-over-Month (MoM) growth for a specific ward and category.
    Refuses un-scoped multi-ward/multi-category queries.
    Flags null rows explicitly.
    """
    if not ward or ward.lower() == "all":
        raise ValueError("REFUSED: All-ward aggregation is not permitted. Scope must be per-ward per-category.")
    if not category or category.lower() == "all":
        raise ValueError("REFUSED: All-category aggregation is not permitted. Scope must be per-ward per-category.")
    if not growth_type or growth_type.lower() != "mom":
        raise ValueError("REFUSED: Growth type must be explicitly specified as MoM.")

    # Filter rows for target ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_actual = None

    for r in filtered:
        period = r["period"]
        budgeted = r["budgeted_amount"]
        actual = r["actual_spend"]
        is_null = r["is_null"]
        notes = r["notes"]

        if is_null:
            mom_str = "NULL"
            formula = "FLAGGED_NULL: Cannot compute growth on null actual_spend"
            flag = "NULL_FLAGGED"
        elif prev_actual is None:
            mom_str = "N/A"
            formula = "Baseline period (Month 1)"
            flag = ""
        else:
            growth_pct = ((actual - prev_actual) / prev_actual) * 100.0
            mom_str = f"{growth_pct:+.1f}%"
            formula = f"({actual} - {prev_actual}) / {prev_actual} * 100"
            flag = ""

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual if actual is not None else "NULL",
            "mom_growth_pct": mom_str,
            "formula": formula,
            "notes": notes,
            "flag": flag,
        })

        if not is_null:
            prev_actual = actual

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific budget category")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)

        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth_pct", "formula", "notes", "flag"]
        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Successfully processed {len(results)} periods for '{args.ward}' - '{args.category}'. Saved to {args.output}")

    except ValueError as e:
        print(f"\n[ENFORCEMENT REFUSAL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

