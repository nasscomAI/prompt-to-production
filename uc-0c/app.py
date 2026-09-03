"""
UC-0C — Number That Looks Right.

Deterministic, offline growth calculator for ward-level infrastructure spend.
It loads a monthly budget CSV, isolates one explicitly requested (ward,
category) slice, flags every deliberately-null actual_spend row with its
verbatim notes reason, and computes period-over-period growth (MoM by default)
showing the formula on every output row. It refuses to aggregate across wards
or categories and refuses to run without an explicit growth type.

Run:
    python app.py \
      --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 – Kasba" \
      --category "Roads & Pothole Repair" \
      --growth-type MoM \
      --output growth_output.csv
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path):
    """Read and validate the budget CSV; return rows and a null-row report."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Input file not found: {0}. Refusing to continue.".format(path)
        )

    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                "Input file {0} is missing required column(s): {1}. "
                "Refusing to continue.".format(path, ", ".join(missing))
            )
        rows = []
        for line_num, record in enumerate(reader, start=2):
            period = record["period"].strip()
            ward = record["ward"].strip()
            category = record["category"].strip()
            budget_raw = record["budgeted_amount"].strip()
            spend_raw = record["actual_spend"].strip()

            try:
                budgeted = float(budget_raw)
            except ValueError:
                budgeted = None

            if spend_raw == "":
                actual = None
            else:
                try:
                    actual = float(spend_raw)
                except ValueError:
                    actual = None

            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": record["notes"].strip(),
                "_line": line_num,
            })

    if not rows:
        raise ValueError("Input file {0} contains no data rows.".format(path))

    null_rows = [r for r in rows if r["actual_spend"] is None]
    return rows, null_rows


def _validate_slice(rows, ward, category):
    """Return only the rows that exactly match the requested ward and category."""
    if ward is None or str(ward).strip() == "":
        raise ValueError(
            "Aggregation across wards is refused: an exact --ward must be "
            "provided. Refusing to aggregate."
        )
    if category is None or str(category).strip() == "":
        raise ValueError(
            "Aggregation across categories is refused: an exact --category must "
            "be provided. Refusing to aggregate."
        )
    selected = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not selected:
        raise ValueError(
            "No rows found for ward={0!r} and category={1!r} in the input. "
            "Refusing to guess; check the exact ward/category strings.".format(ward, category)
        )
    selected.sort(key=lambda r: r["period"])
    return selected


def compute_growth(rows, ward, category, growth_type):
    """Return a per-period growth table for one (ward, category) slice."""
    if growth_type is None or str(growth_type).strip() == "":
        raise ValueError(
            "--growth-type was not specified. Refusing to guess: please specify "
            "an explicit growth type such as MoM (month-over-month) or YoY "
            "(year-over-year)."
        )
    growth_type = growth_type.strip().upper()
    if growth_type not in ("MOM", "YOY"):
        raise ValueError(
            "Unsupported --growth-type {0!r}. Supported: MoM, YoY. Refusing to guess.".format(growth_type)
        )

    selected = _validate_slice(rows, ward, category)

    table = []
    for idx, row in enumerate(selected):
        current = row["actual_spend"]

        if current is None:
            table.append({
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": "",
                "previous_actual_spend": "",
                "growth_percent": "",
                "formula": "",
                "status": "NULL / NOT COMPUTED",
                "notes": row["notes"] or "actual_spend is blank",
            })
            continue

        previous = None
        if idx >= 1:
            previous = selected[idx - 1]["actual_spend"]

        if growth_type == "MOM":
            if previous is None:
                growth_percent = ""
                formula = "first period: no previous {0} value to compare".format(growth_type)
            else:
                if previous == 0:
                    growth_percent = ""
                    formula = "previous actual_spend is zero: growth undefined"
                else:
                    growth_percent = round((current - previous) / previous * 100.0, 1)
                    formula = "({0} - {1})/{1} x 100 = {2}%".format(
                        _fmt(current), _fmt(previous), _fmt_signed(growth_percent)
                    )
        else:  # YoY
            growth_percent = ""
            formula = "YoY requires a previous-year baseline which this dataset lacks; not computed"

        table.append({
            "ward": row["ward"],
            "category": row["category"],
            "period": row["period"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": _fmt(current),
            "previous_actual_spend": _fmt(previous) if previous is not None else "",
            "growth_percent": growth_percent,
            "formula": formula,
            "status": "OK",
            "notes": row["notes"],
        })

    return table


def _fmt(value):
    """Format a float for display, trimming trailing zeros."""
    if value is None:
        return ""
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def _fmt_signed(value):
    return ("{0:+.1f}".format(value)).rstrip("0").rstrip(".")


def write_output(table, output_path):
    fieldnames = [
        "ward", "category", "period", "budgeted_amount", "actual_spend",
        "previous_actual_spend", "growth_percent", "formula", "status", "notes",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in table:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic ward-level spend growth calculator (UC-0C)."
    )
    parser.add_argument("--input", default="../data/budget/ward_budget.csv")
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type")
    parser.add_argument("--output", default="growth_output.csv")
    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print("ERROR: {0}".format(exc), file=sys.stderr)
        sys.exit(1)

    print("Loaded {0} rows from {1}".format(len(rows), args.input))
    print("Null actual_spend rows: {0}".format(len(null_rows)))
    for r in sorted(null_rows, key=lambda x: (x["_line"])):
        print("  NULL: {0} | {1} | {2} | notes: {3}".format(
            r["period"], r["ward"], r["category"], r["notes"] or "(blank)"
        ))

    try:
        table = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print("REFUSED: {0}".format(exc), file=sys.stderr)
        sys.exit(1)

    write_output(table, args.output)
    print("Wrote per-ward per-category growth table to: {0}".format(args.output))


if __name__ == "__main__":
    main()
