"""
UC-0C app.py — Number That Looks Right
Built per agents.md (RICE enforcement) and skills.md (load_dataset, compute_growth).
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
AGGREGATION_VALUES = {"", "all", "*"}


def load_dataset(input_path: str) -> list:
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows
    before any computation happens.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required column(s) in {input_path}: {sorted(missing)}")
        rows = list(reader)

    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    print(f"load_dataset: {len(rows)} rows loaded, {len(null_rows)} null actual_spend row(s):")
    for r in null_rows:
        print(f"  {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes']}")

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter to one ward + one category, return per-period table with formula
    shown. Refuses instead of guessing on aggregation, missing growth_type,
    unsupported growth_type, or unknown ward/category.
    """
    if not growth_type:
        raise ValueError(
            "REFUSED: --growth-type not specified. Must be MoM. "
            "Never guessing which formula you want."
        )
    if growth_type != "MoM":
        raise ValueError(
            f"REFUSED: growth-type '{growth_type}' is not supported. "
            "This dataset covers only calendar year 2024 — there is no prior-year "
            "data to compute YoY against. Only MoM is computable here."
        )
    if ward.strip().lower() in AGGREGATION_VALUES or category.strip().lower() in AGGREGATION_VALUES:
        raise ValueError(
            "REFUSED: aggregation across wards/categories was requested (blank or 'All'). "
            "This system only reports one ward + one category at a time — never silently aggregates."
        )

    series = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not series:
        raise ValueError(
            f"REFUSED: no rows found for ward='{ward}' category='{category}'. "
            "Check exact spelling (including the en-dash in ward names) rather than guessing the closest match."
        )

    series.sort(key=lambda r: r["period"])

    results = []
    prev_value = None
    for row in series:
        period = row["period"]
        budgeted = row["budgeted_amount"]
        raw_spend = row["actual_spend"].strip()

        if not raw_spend:
            results.append({
                "period": period,
                "budgeted_amount": budgeted,
                "actual_spend": "",
                "formula": "NOT COMPUTED",
                "growth_pct": "",
                "note": f"NULL actual_spend — {row['notes']}",
            })
            prev_value = None  # null breaks the MoM chain for the following period too
            continue

        current = float(raw_spend)

        if prev_value is None:
            results.append({
                "period": period,
                "budgeted_amount": budgeted,
                "actual_spend": raw_spend,
                "formula": "NOT COMPUTED",
                "growth_pct": "",
                "note": "No valid prior period to compute MoM against",
            })
        else:
            growth = (current - prev_value) / prev_value * 100
            formula = f"({current}-{prev_value})/{prev_value}"
            results.append({
                "period": period,
                "budgeted_amount": budgeted,
                "actual_spend": raw_spend,
                "formula": formula,
                "growth_pct": f"{growth:.1f}%",
                "note": "",
            })

        prev_value = current

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", default=None, help="MoM (only supported type)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows = load_dataset(args.input)

    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["period", "budgeted_amount", "actual_spend", "formula", "growth_pct", "note"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()
