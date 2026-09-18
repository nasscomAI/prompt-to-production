"""UC-0C app.py — Ward budget growth calculator.

Loads the ward budget CSV, flags every null row with its notes reason before
computing, and produces a per-ward/per-category per-period growth table with
the formula shown on every row. Never aggregates across wards or categories,
never guesses a growth type, and never computes on null spend.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

SUPPORTED_GROWTH_TYPES = {"MoM"}
FORMULA_TEMPLATES = {"MoM": "((current / previous) - 1) * 100"}


def _parse_float(value: str):
    value = (value or "").strip()
    return float(value) if value else None


def _previous_month(period: str) -> str:
    """Return the calendar month preceding period (YYYY-MM)."""
    year, month = (int(x) for x in period.split("-"))
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1
    return f"{year:04d}-{month:02d}"


def load_dataset(input_path: str) -> tuple:
    """Read the ward budget CSV and validate its columns.

    Returns (rows, null_report) where rows are dict-like records with
    actual_spend parsed to float or None, and null_report lists every row whose
    actual_spend is blank, including its notes reason. Raises ValueError if the
    file is missing or required columns are absent.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            raw_rows = list(reader)
    except FileNotFoundError:
        raise ValueError(f"input file not found: {input_path}")
    except Exception as exc:
        raise ValueError(f"could not read input file {input_path}: {exc}")

    if not raw_rows:
        raise ValueError(f"input file is empty: {input_path}")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in raw_rows[0]]
    if missing_cols:
        raise ValueError(f"missing required columns: {', '.join(missing_cols)}")

    rows = []
    for raw in raw_rows:
        record = dict(raw)
        record["budgeted_amount"] = _parse_float(record["budgeted_amount"])
        record["actual_spend"] = _parse_float(record["actual_spend"])
        rows.append(record)

    null_report = [
        {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "notes": (r["notes"] or "").strip(),
        }
        for r in rows
        if r["actual_spend"] is None
    ]
    return rows, null_report


def _validate_growth_type(growth_type: str) -> str:
    """Return the canonical growth type or raise ValueError (refuse instead of
    guessing). An unspecified or unsupported growth type refuses."""
    if not growth_type or not growth_type.strip():
        raise ValueError(
            "ERROR: --growth-type is required. Supported: MoM. "
            "Refusing to guess a formula."
        )
    canonical = growth_type.strip()
    if canonical not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            f"ERROR: unsupported --growth-type '{canonical}'. Supported: "
            f"MoM. YoY is not computable from this dataset because it contains "
            f"only 2024 data with no prior-year baseline."
        )
    return canonical


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Return a per-period growth table for one ward+category slice.

    Every row shows the formula used. Rows with a null spend (current or
    previous month) are flagged with their status and never computed. Refuses
    (ValueError) if the ward/category combination is absent from the data.
    """
    growth_type = _validate_growth_type(growth_type)

    slice_rows = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    if not slice_rows:
        raise ValueError(
            f"ERROR: no data for ward '{ward}' + category '{category}'. "
            f"Refusing to aggregate across wards or categories."
        )

    slice_rows.sort(key=lambda r: r["period"])
    results = []
    for index, row in enumerate(slice_rows):
        period = row["period"]
        current = row["actual_spend"]
        notes = (row["notes"] or "").strip()

        if current is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": "",
                "status": "NULL_ACTUAL_SPEND (not computed)",
                "notes": notes or "actual_spend is blank",
            })
            continue

        previous_month = _previous_month(period)
        prev = None
        prev_period = ""
        if index == 0:
            status = "NO_PREVIOUS_PERIOD (first month; growth not computed)"
        else:
            prev_row = slice_rows[index - 1]
            previous = prev_row["actual_spend"]
            prev_period = prev_row["period"]
            if prev_period != previous_month:
                status = "PERIOD_GAP (previous calendar month absent; not computed)"
            elif previous is None:
                status = "PREVIOUS_MONTH_NULL (not computed)"
            else:
                prev = previous
                status = "COMPUTED"

        if prev is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current,
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": f"(using {growth_type})",
                "status": status,
                "notes": notes,
            })
            continue

        growth = (current / prev - 1) * 100
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current,
            "growth_type": growth_type,
            "growth_percent": f"{growth:+.1f}",
            "formula": f"(({current}/{prev})-1)*100",
            "status": "COMPUTED",
            "notes": notes,
        })
    return results


def _print_null_report(null_report: list):
    print(f"Null rows flagged before computing ({len(null_report)}):")
    for item in null_report:
        print(
            f"  {item['period']} | {item['ward']} | {item['category']} | "
            f"notes: {item['notes'] or '(no reason given)'}"
        )


def write_output(output_path: str, results: list):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "notes",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category (exact match)")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write the growth table")
    args = parser.parse_args()

    try:
        rows, null_report = load_dataset(args.input)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    _print_null_report(null_report)

    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    write_output(args.output, results)

    computed = sum(1 for r in results if r["status"] == "COMPUTED")
    flagged = sum(1 for r in results if r["status"] != "COMPUTED")
    print(
        f"Done. Per-period growth table ({len(results)} rows: "
        f"{computed} computed, {flagged} flagged) written to {args.output}"
    )


if __name__ == "__main__":
    main()