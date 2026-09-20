"""
UC-0C — Budget Growth That Is Wrong
Vibe-coded from agents.md + skills.md (RICE -> CRAFT workflow).

Enforcement rules from agents.md are implemented here:
  1. Aggregation is always per-ward AND per-category (cross-ward totals refused).
  2. Growth type is mandatory and must be MoM or YoY.
  3. Blank actual_spend -> NULL growth, null_flag=YES, note preserved.
  4. Every figure carries its formula string.
  5. Explicit --ward/--category must match the dataset or the run is refused.
"""
import argparse
import csv
import os
import sys

GROWTH_TYPES = ("MoM", "YoY")
REQUIRED_COLUMNS = ("period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes")
# Values that would request cross-ward / cross-category aggregation.
AGGREGATE_TOKENS = {"all", "total", "whole", "aggregate", "entire"}


class RefusalError(Exception):
    """Raised when a requested operation is refused by the enforcement rules."""


def load_dataset(input_path: str):
    """Read and validate the budget CSV; return rows, wards, categories, nulls."""
    if not os.path.exists(input_path):
        raise RefusalError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8-sig", newline="") as filehandle:
        reader = csv.DictReader(filehandle)
        header = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in header]
        if missing:
            raise RefusalError(f"Dataset is missing required column(s): {missing}")
        rows = [dict(row) for row in reader]

    if not rows:
        raise RefusalError("Dataset is empty; cannot compute growth.")

    days = {"budgeted_amount", "actual_spend"}
    null_report = []
    for row in rows:
        for column in days:
            raw = str(row.get(column, "") or "").strip()
            row[column] = None if raw == "" else float(raw)
        notes = str(row.get("notes") or "").strip()
        row["notes"] = notes
        if row["actual_spend"] is None:
            null_report.append(row)

    wards = sorted({row["ward"] for row in rows})
    categories = sorted({row["category"] for row in rows})
    return rows, wards, categories, null_report


def _refuse_scope(ward, category, available_wards, available_categories):
    """Sanity-check explicit --ward/--category values against the dataset."""
    if ward is None and category is None:
        return
    if ward is not None:
        lowered = ward.lower()
        if lowered in AGGREGATE_TOKENS:
            raise RefusalError(
                f"Cross-ward aggregation is refused. Provide one ward or omit "
                f"--ward to produce the full per-ward x per-category table.")
        if ward not in available_wards:
            raise RefusalError(
                f"Ward '{ward}' is not in the dataset. Available wards: "
                f"{', '.join(available_wards)}")
    if category is not None:
        lowered = category.lower()
        if lowered in AGGREGATE_TOKENS:
            raise RefusalError(
                f"Cross-category aggregation is refused. Provide one category or "
                f"omit --category to produce the full per-ward x per-category table.")
        if category not in available_categories:
            raise RefusalError(
                f"Category '{category}' is not in the dataset. Available "
                f"categories: {', '.join(available_categories)}")


def _grow(current, previous):
    """Return rounded growth percent, or None when it cannot be computed."""
    if previous is None or previous == 0.0:
        return None
    value = (current - previous) / previous * 100
    return None if value != value or value in (float("inf"), float("-inf")) else round(value, 1)


def _match(key, rows):
    return [row for row in rows if row["ward"] == key[0] and row["category"] == key[1]]


def compute_growth(rows, growth_type: str):
    """Compute growth per period for every ward x category series."""
    keys = sorted({(row["ward"], row["category"]) for row in rows})
    results = []
    for key in keys:
        series = sorted(_match(key, rows), key=lambda row: row["period"])
        for index, row in enumerate(series):
            current = row["actual_spend"]
            previous = None
            if growth_type == "MoM":
                if index > 0:
                    previous = series[index - 1]["actual_spend"]
                formula = "MoM = (current - previous) / previous * 100"
            else:  # YoY
                year, month = row["period"].split("-")
                prev_year = f"{int(year) - 1:04d}-{month}"
                prev_row = next(
                    (r for r in series if r["period"] == prev_year), None)
                if prev_row is not None:
                    previous = prev_row["actual_spend"]
                formula = "YoY = (current - previous) / previous * 100"

            growth = _grow(current, previous) if current is not None else None
            if current is None:
                flag, note = "YES", row["notes"] or "actual_spend is blank in source data"
                growth_pct = ""
            elif growth is None:
                flag = "NEEDS_REVIEW"
                note = "no prior-period value available"
                growth_pct = ""
            else:
                flag, note = "", row["notes"]
                growth_pct = growth

            results.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": row["actual_spend"],
                "growth_pct": growth_pct,
                "growth_type": growth_type,
                "formula": formula,
                "null_flag": flag,
                "note": note,
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C per-ward per-category budget growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="One ward (or omit for full table)")
    parser.add_argument("--category", default=None, help="One category (or omit for full table)")
    parser.add_argument("--growth-type", default=None, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("Refused: --growth-type is mandatory. Use --growth-type MoM or YoY.",
              file=sys.stderr)
        sys.exit(1)
    if args.growth_type not in GROWTH_TYPES:
        print(f"Refused: unsupported growth type '{args.growth_type}'. "
              f"Supported types: {', '.join(GROWTH_TYPES)}.", file=sys.stderr)
        sys.exit(1)

    rows, wards, categories, null_report = load_dataset(args.input)

    try:
        _refuse_scope(args.ward, args.category, wards, categories)
    except RefusalError as error:
        print(f"Refused: {error}", file=sys.stderr)
        sys.exit(1)

    scope = "full per-ward x per-category table"
    if args.ward and args.category:
        scope = f"ward='{args.ward}', category='{args.category}'"
        rows = [row for row in rows
                if row["ward"] == args.ward and row["category"] == args.category]
    elif args.ward:
        scope = f"ward='{args.ward}', all categories"
        rows = [row for row in rows if row["ward"] == args.ward]
    elif args.category:
        scope = f"all wards, category='{args.category}'"
        rows = [row for row in rows if row["category"] == args.category]

    results = compute_growth(rows, args.growth_type)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "growth_pct", "growth_type", "formula", "null_flag", "note"]
    with open(args.output, "w", encoding="utf-8", newline="") as filehandle:
        writer = csv.DictWriter(filehandle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    null_count = len(null_report) if not (args.ward or args.category) else \
        sum(row["actual_spend"] is None for row in rows)

    print(f"Done. Growth written to {args.output}")
    print(f"Scope: {scope} ({len(results)} periods)")
    print(f"Null rows in scope: {null_count} -> marked null_flag=YES, never dropped")
    print("Null report:")
    for report_row in null_report:
        if (not args.ward or report_row["ward"] == args.ward) and \
           (not args.category or report_row["category"] == args.category):
            print(f"  {report_row['period']} | {report_row['ward']} | "
                  f"{report_row['category']} | note: "
                  f"{report_row['notes'] or '(empty)'}")


if __name__ == "__main__":
    main()