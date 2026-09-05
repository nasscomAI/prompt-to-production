"""
UC-0C app.py — Number That Looks Right.
Computes per-ward, per-category month-over-month or year-over-year growth
from ward_budget.csv. Flags null rows, shows the formula, and refuses to
aggregate or guess the growth type.
Built from uc-0c/agents.md and uc-0c/skills.md (RICE).
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]


def load_dataset(input_path: str):
    """Read the CSV, validate columns, and report null rows."""
    with open(input_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise SystemExit("Input CSV has no header row.")
        for col in REQUIRED_COLUMNS:
            if col not in reader.fieldnames:
                raise SystemExit(f"Missing required column: {col}")
        dataset = []
        for row in reader:
            row["actual_spend"] = row["actual_spend"].strip()
            row["budgeted_amount"] = row["budgeted_amount"].strip()
            dataset.append(row)

    nulls = [r for r in dataset if r["actual_spend"] == ""]
    total = len(dataset)
    print(f"Loaded {total} rows. Null actual_spend rows: {len(nulls)} ...")
    for r in nulls:
        print(f"  NULL {r['period']} | {r['ward']} | {r['category']} | "
              f"note: {r['notes'] or '(no note)'}")
    return dataset, nulls


def compute_growth(dataset, ward: str, category: str, growth_type: str,
                   output_path: str):
    """Compute a per-month growth table for one ward + category."""
    growth_type = growth_type.strip().lower()
    if growth_type not in ("mom", "yoy"):
        raise SystemExit(
            f"Unknown --growth-type '{growth_type}'. Use 'MoM' or 'YoY'. "
            "Refusing to guess.")

    rows = [r for r in dataset
            if r["ward"] == ward and r["category"] == category]
    if not rows:
        raise SystemExit(
            f"No data for ward '{ward}' and category '{category}'. Refusing.")

    rows.sort(key=lambda r: r["period"])

    if growth_type == "mom":
        formula = "MoM = (this_month_actual / prev_month_actual - 1) * 100"
    else:
        formula = "YoY = (this_period_actual / same_period_prev_year - 1) * 100"

    # Map period -> actual for previous-year lookups (YoY).
    by_period = {}
    for r in dataset:
        if r["ward"] == ward and r["category"] == category:
            if r["actual_spend"] != "":
                by_period[r["period"]] = float(r["actual_spend"])

    out_rows = []
    prev_actual = None
    for r in rows:
        period = r["period"]
        null_reason = r["notes"] if r["actual_spend"] == "" else ""
        prev_period = _prev_period(period) if growth_type == "mom" \
            else _prev_year_period(period)
        prev_val = by_period.get(prev_period)

        if r["actual_spend"] == "":
            out_rows.append({"period": period, "actual_spend": "",
                             "formula": formula, "growth_type": growth_type,
                             "growth_result": "", "null_reason": null_reason,
                             "flagged": "NULL"})
        elif growth_type == "mom" and prev_actual is None:
            out_rows.append({"period": period,
                             "actual_spend": r["actual_spend"],
                             "formula": formula, "growth_type": growth_type,
                             "growth_result": "(no prior month)",
                             "null_reason": "", "flagged": ""})
        elif prev_val is None:
            out_rows.append({"period": period,
                             "actual_spend": r["actual_spend"],
                             "formula": formula, "growth_type": growth_type,
                             "growth_result": "(no base period)",
                             "null_reason": "", "flagged": ""})
        else:
            curr = float(r["actual_spend"])
            growth = round((curr / prev_val - 1) * 100, 1)
            out_rows.append({"period": period, "actual_spend": r["actual_spend"],
                             "formula": formula, "growth_type": growth_type,
                             "growth_result": f"{growth:+}%",
                             "null_reason": "", "flagged": ""})
        if r["actual_spend"] != "":
            prev_actual = float(r["actual_spend"])

    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["period", "actual_spend", "formula", "growth_type",
                            "growth_result", "null_reason", "flagged"])
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\nWard: {ward}\nCategory: {category}\nGrowth type: {growth_type}")
    print(f"Formula: {formula}")
    print(f"Done. Growth table written to {output_path}")
    flagged = [o for o in out_rows if o["flagged"]]
    if flagged:
        print(f"Flagged {len(flagged)} null row(s) — not computed.")


def _prev_period(period: str):
    year, month = period.split("-")
    month = int(month) - 1
    if month == 0:
        month = 12
        year = int(year) - 1
    return f"{int(year):04d}-{month:02d}"


def _prev_year_period(period: str):
    year, month = period.split("-")
    return f"{int(year) - 1:04d}-{month}"


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False,
                        help="MoM or YoY (required; refusing to guess)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    if args.growth_type is None:
        raise SystemExit(
            "No --growth-type specified. Refusing to guess — provide 'MoM' "
            "or 'YoY'.")

    dataset, nulls = load_dataset(args.input)

    if args.ward.lower() in ("all", "total", "*") or \
       (args.category and args.category.lower() in ("all", "total", "*")):
        raise SystemExit(
            "All-ward or all-category aggregation requested. Refusing — only "
            "per-ward per-category growth is supported.")

    if not args.category:
        raise SystemExit(
            "No --category specified. Refusing to aggregate — provide one "
            "category name.")

    compute_growth(dataset, args.ward, args.category, args.growth_type,
                   args.output)


if __name__ == "__main__":
    main()