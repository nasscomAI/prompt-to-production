"""
UC-0C — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os


def load_dataset(csv_path):
    """Reads ward_budget.csv, validates columns, reports null count and which rows before returning structured data."""
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    missing = [c for c in required_columns if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}. Available: {reader.fieldnames}")

    null_rows = []
    for i, row in enumerate(rows):
        try:
            spend = float(row["actual_spend"]) if row["actual_spend"] else None
        except (ValueError, TypeError):
            spend = None
        if spend is None:
            null_rows.append(i)

    return {
        "columns": required_columns,
        "rows": rows,
        "null_count": len(null_rows),
        "null_rows": null_rows,
        "notes": {i: row["notes"] for i, row in enumerate(rows) if i in null_rows},
    }


def compute_growth(dataset, ward, category, growth_type):
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    rows = dataset["rows"]

    matching = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not matching:
        available_wards = sorted(set(r["ward"] for r in rows))
        available_categories = sorted(set(r["category"] for r in rows))
        raise ValueError(
            f"Ward '{ward}' or category '{category}' not found. "
            f"Available wards: {available_wards[:5]}... Available categories: {available_categories[:5]}..."
        )

    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")

    # Sort by period
    period_order = sorted(set(r["period"] for r in rows))
    matching_sorted = sorted(matching, key=lambda r: r["period"])

    # Build a map of period -> actual_spend for matching ward+category
    spend_map = {}
    for r in matching_sorted:
        period = r["period"]
        actual = r["actual_spend"]
        try:
            spend_val = float(actual) if actual else None
        except (ValueError, TypeError):
            spend_val = None
        spend_map[period] = spend_val

    output = []
    for i, period in enumerate(period_order):
        actual = spend_map.get(period)
        prev_period = period_order[i - 1] if i > 0 else None
        prev_actual = spend_map.get(prev_period) if prev_period else None

        if actual is None:
            formula = "null — no data"
            growth_value = None
        else:
            if growth_type == "MoM":
                if prev_actual is None or prev_actual == 0:
                    formula = f"MoM: actual={actual}, previous=null/0"
                    growth_value = None
                else:
                    growth = (actual - prev_actual) / abs(prev_actual) * 100
                    formula = f"MoM: ({actual} - {prev_actual}) / |{prev_actual}| * 100"
                    growth_value = round(growth, 1)
            else:  # YoY
                # Find same period previous year
                yoy_period = None
                for p in period_order:
                    if p == period:
                        yoy_period = period_order[period_order.index(p) - 12] if period_order.index(p) >= 12 else None
                        break
                if yoy_period is None or yoy_period not in spend_map:
                    formula = f"YoY: actual={actual}, previous year data unavailable"
                    growth_value = None
                else:
                    yoy_actual = spend_map[yoy_period]
                    if yoy_actual is None or yoy_actual == 0:
                        formula = f"YoY: actual={actual}, previous year null/0"
                        growth_value = None
                    else:
                        growth = (actual - yoy_actual) / abs(yoy_actual) * 100
                        formula = f"YoY: ({actual} - {yoy_actual}) / |{yoy_actual}| * 100"
                        growth_value = round(growth, 1)

        output.append({
            "period": period,
            "actual_spend": actual if actual is not None else "",
            "formula": formula,
            "growth_value_pct": growth_value,
        })

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    result = compute_growth(dataset, args.ward, args.category, args.growth_type)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True) if os.path.dirname(args.output) else None

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "formula", "growth_value_pct"])
        writer.writeheader()
        for row in result:
            writer.writerow({
                "period": row["period"],
                "actual_spend": row["actual_spend"],
                "formula": row["formula"],
                "growth_value_pct": row["growth_value_pct"] if row["growth_value_pct"] is not None else "",
            })

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
