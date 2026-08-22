"""
UC-0C app.py — Municipal budget growth agent.
Computes period-over-period growth of actual_spend for ONE ward and ONE category,
per agents.md and skills.md. See README.md for the run command and reference values.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ("MoM", "YoY")
AGGREGATION_TOKENS = {"all", "*", "", "any", "total", "aggregate"}
FORMULA_TEMPLATES = {
    "MoM": "MoM = (curr - prev) / prev x 100",
    "YoY": "YoY = (curr - prev_year_same_month) / prev_year_same_month x 100",
}


class Refusal(Exception):
    pass


def load_dataset(path):
    try:
        f = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise Refusal(f"Cannot read input file '{path}': {exc}")
    with f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise Refusal(
                f"Input CSV is missing required columns {missing}; "
                f"expected columns: {REQUIRED_COLUMNS}"
            )
        rows = [
            {
                "period": r["period"].strip(),
                "ward": r["ward"].strip(),
                "category": r["category"].strip(),
                "budgeted_amount": r["budgeted_amount"].strip(),
                "actual_spend": r["actual_spend"].strip(),
                "notes": r["notes"],
            }
            for r in reader
        ]
    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    periods = sorted({r["period"] for r in rows})
    nulls = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"], "notes": r["notes"]}
        for r in rows
        if not r["actual_spend"]
    ]
    return {"rows": rows, "wards": wards, "categories": categories, "periods": periods, "nulls": nulls}


def validate_target(ward, category, dataset):
    for label, value, valid in (
        ("--ward", ward, dataset["wards"]),
        ("--category", category, dataset["categories"]),
    ):
        if value.strip().lower() in AGGREGATION_TOKENS:
            raise Refusal(
                f"REFUSED: '{value}' would aggregate across {'wards' if label == '--ward' else 'categories'}. "
                "This agent computes exactly ONE ward x ONE category. "
                f"Valid {label} options: {valid}"
            )
        if value not in valid:
            raise Refusal(
                f"REFUSED: {label} '{value}' does not exactly match any value in the CSV. "
                f"Valid options: {valid}"
            )


def validate_growth_type(growth_type):
    if not growth_type or not growth_type.strip():
        raise Refusal(
            "REFUSED: --growth-type was not specified. Which type is intended: MoM "
            "(month-over-month) or YoY (year-over-year)? No default is applied."
        )
    gt = growth_type.strip().upper()
    if gt not in ("MOM", "YOY"):
        raise Refusal(f"REFUSED: unknown --growth-type '{growth_type}'. Valid options: ['MoM', 'YoY']")
    return {"MOM": "MoM", "YOY": "YoY"}[gt]


def _spend(rows_by_period, period):
    raw = rows_by_period[period]["actual_spend"]
    return float(raw) if raw else None


def compute_growth(dataset, ward, category, growth_type):
    relevant = [r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category]
    rows_by_period = {r["period"]: r for r in relevant}
    template = FORMULA_TEMPLATES[growth_type]

    def predecessor(period):
        year, month = int(period[:4]), int(period[5:7])
        if growth_type == "MoM":
            month -= 1
            if month == 0:
                year, month = year - 1, 12
        else:
            year -= 1
        return f"{year:04d}-{month:02d}"

    table = []
    for period in dataset["periods"]:
        row = rows_by_period.get(period)
        if row is None:
            table.append({
                "period": period, "actual_spend": "NULL", "formula_used": template,
                "growth_pct": "", "flag": "no data row for this ward/category",
            })
            continue
        if not row["actual_spend"]:
            table.append({
                "period": period, "actual_spend": "NULL", "formula_used": template,
                "growth_pct": "",
                "flag": f"NULL actual_spend — not computed; notes: \"{row['notes']}\"",
            })
            continue
        curr = float(row["actual_spend"])
        prev_period = predecessor(period)
        prev_row = rows_by_period.get(prev_period)
        prev = _spend(rows_by_period, prev_period) if prev_row else None
        if prev is None:
            reason = (
                f"predecessor {prev_period} is NULL"
                if prev_row
                else f"no {growth_type} predecessor period ({prev_period}) in dataset"
            )
            table.append({
                "period": period, "actual_spend": curr, "formula_used": template,
                "growth_pct": "", "flag": f"growth not computable: {reason}",
            })
            continue
        growth = round((curr - prev) / prev * 100, 1)
        shown = f"{template}: ({curr} - {prev}) / {prev} x 100"
        table.append({
            "period": period, "actual_spend": curr, "formula_used": shown,
            "growth_pct": growth, "flag": "",
        })
    return table


def write_output(path, table, ward, category):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ward", "category"] + ["period", "actual_spend", "formula_used", "growth_pct", "flag"])
        for row in table:
            writer.writerow([ward, category, row["period"], row["actual_spend"],
                             row["formula_used"], row["growth_pct"], row["flag"]])


def main(argv=None):
    parser = argparse.ArgumentParser(description="UC-0C ward/category spend growth agent")
    parser.add_argument("--input", required=True, help="path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="exact ward name as it appears in the CSV")
    parser.add_argument("--category", required=True, help="exact category name as it appears in the CSV")
    parser.add_argument("--growth-type", default=None, choices=None,
                        help="REQUIRED: MoM or YoY — no default is applied")
    parser.add_argument("--output", default="growth_output.csv", help="output CSV path")
    args = parser.parse_args(argv)

    try:
        dataset = load_dataset(args.input)

        print(f"Loaded {len(dataset['rows'])} rows | wards={dataset['wards']} | "
              f"categories={dataset['categories']}")
        print(f"Null actual_spend rows found BEFORE any computation: {len(dataset['nulls'])}")
        for n in dataset["nulls"]:
            print(f"  NULL: {n['period']} | {n['ward']} | {n['category']} | notes: \"{n['notes']}\"")

        validate_growth_type(args.growth_type)
        validate_target(args.ward, args.category, dataset)

        table = compute_growth(dataset, args.ward, args.category, args.growth_type)
        write_output(args.output, table, args.ward, args.category)

        print(f"\nGrowth table for '{args.ward}' / '{args.category}' ({args.growth_type.upper()}):")
        for row in table:
            flag = f"  [{row['flag']}]" if row["flag"] else ""
            print(f"  {row['period']} | spend={row['actual_spend']} | "
                  f"growth={row['growth_pct'] or 'n/a'}% | {row['formula_used']}{flag}")
        print(f"\nWrote {len(table)} rows to {args.output}")
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
