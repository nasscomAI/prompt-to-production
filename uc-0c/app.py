import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_COLUMNS = ["period", "ward", "category", "actual_spend", "growth_result", "formula", "notes"]
GROWTH_TYPES = ("MoM", "YoY")
AGGREGATE_TERMS = {"all", "*", "any", "total", "aggregate", "aggregated", "overall", "citywide", ""}
NULL_STATUS = "NULL — not computed"


def normalize(value):
    return " ".join(str(value).replace("\u2013", "-").replace("\u2014", "-").lower().split())


def fail(message, kind="ERROR"):
    print(f"{kind}: {message}", file=sys.stderr)
    raise SystemExit(2)


def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0C: MoM/YoY budget growth for exactly one ward x one category."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name from the dataset")
    parser.add_argument("--category", required=True, help="Exact category name from the dataset")
    parser.add_argument(
        "--growth-type",
        choices=GROWTH_TYPES,
        help="MoM or YoY. Refuses to run if omitted — never guesses.",
    )
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()
    if args.growth_type is None:
        parser.error(
            "--growth-type is required (MoM or YoY). Refusing to guess — please specify it and re-run."
        )
    return args


def guard_aggregation(args):
    for label, value in (("ward", args.ward), ("category", args.category)):
        if normalize(value) in AGGREGATE_TERMS:
            fail(
                f"Refusing to aggregate: '{label}' cannot be '{value}'. "
                "This tool computes one ward x one category at a time; "
                "aggregation across wards or categories is not supported.",
                kind="REFUSED",
            )


def parse_period(period):
    parts = str(period).strip().split("-")
    if len(parts) != 2:
        fail(f"Invalid period '{period}' — expected YYYY-MM.")
    try:
        year, month = int(parts[0]), int(parts[1])
    except ValueError:
        fail(f"Invalid period '{period}' — expected YYYY-MM.")
    if not 1 <= month <= 12:
        fail(f"Invalid month in period '{period}' — expected YYYY-MM.")
    return year, month


def shift_period(year, month, offset):
    total = year * 12 + (month - 1) + offset
    return total // 12, total % 12 + 1


def load_dataset(path):
    try:
        handle = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        fail(f"Cannot read input file '{path}': {exc}")
    with handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            fail(f"Input CSV is missing required columns: {', '.join(missing)}")
        rows = []
        for line_number, record in enumerate(reader, start=2):
            for column in ("period", "ward", "category"):
                if not (record.get(column) or "").strip():
                    fail(f"Line {line_number}: empty '{column}' value.")
            parse_period(record["period"])
            record["actual_spend_raw"] = (record.get("actual_spend") or "").strip()
            for column in ("budgeted_amount", "actual_spend"):
                raw = (record.get(column) or "").strip()
                if raw == "":
                    record[column] = None
                else:
                    try:
                        record[column] = float(raw)
                    except ValueError:
                        fail(f"Line {line_number}: '{column}' is not numeric: '{raw}'")
            record["notes"] = (record.get("notes") or "").strip()
            rows.append(record)
    if not rows:
        fail("Input CSV contains no data rows.")
    return rows


def report_nulls(rows):
    null_rows = [row for row in rows if row["actual_spend"] is None]
    print(f"[null-report] dataset rows={len(rows)} | null actual_spend={len(null_rows)}")
    for row in null_rows:
        reason = row["notes"] or "no reason given"
        print(
            f"[null-report] flagged BEFORE computing: {row['period']} | "
            f"{row['ward']} | {row['category']} | reason: {reason}"
        )
    return null_rows


def select_series(rows, ward, category):
    target_ward, target_category = normalize(ward), normalize(category)
    series = [
        row
        for row in rows
        if normalize(row["ward"]) == target_ward and normalize(row["category"]) == target_category
    ]
    if not series:
        known_wards = "\n  ".join(sorted({row["ward"] for row in rows}))
        known_categories = "\n  ".join(sorted({row["category"] for row in rows}))
        fail(
            f"No data for ward='{ward}' category='{category}'.\n"
            f"Known wards:\n  {known_wards}\nKnown categories:\n  {known_categories}",
            kind="REFUSED",
        )
    return series


def compute_growth(series, growth_type):
    offset = -1 if growth_type == "MoM" else -12
    by_period = {}
    for row in series:
        by_period[parse_period(row["period"])] = row

    results = []
    for (year, month), row in sorted(by_period.items()):
        current = row["actual_spend"]
        previous_key = shift_period(year, month, offset)
        previous_row = by_period.get(previous_key)
        previous = previous_row["actual_spend"] if previous_row else None
        current_text = row["actual_spend_raw"]
        previous_text = previous_row["actual_spend_raw"] if previous_row else ""

        growth_result, formula = "", ""
        if current is None:
            growth_result = NULL_STATUS
        elif previous_row is None:
            growth_result = "N/A (no prior period)" if growth_type == "MoM" else "N/A (no prior year)"
        elif previous is None:
            growth_result = "N/A (previous period spend is null)"
        else:
            delta = (current - previous) / previous * 100
            growth_result = f"{delta:+.1f}%"
            formula = f"({current_text} - {previous_text}) / {previous_text} * 100 = {growth_result}"

        results.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_text,
                "growth_result": growth_result,
                "formula": formula,
                "notes": row["notes"],
            }
        )
    return results


def write_output(results, path):
    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(results)
    except PermissionError:
        fail(
            f"Cannot write '{path}' — permission denied. The file is most likely open in "
            "Excel or another program; close it there, or pass a different --output path.",
            kind="ERROR",
        )


def main():
    args = parse_args()
    guard_aggregation(args)
    rows = load_dataset(args.input)
    report_nulls(rows)
    series = select_series(rows, args.ward, args.category)
    results = compute_growth(series, args.growth_type)
    write_output(results, args.output)

    computed = sum(1 for result in results if result["formula"])
    null_flagged = sum(1 for result in results if result["growth_result"] == NULL_STATUS)
    skipped = len(results) - computed - null_flagged
    print(
        f"[summary] growth_type={args.growth_type} periods={len(results)} "
        f"computed={computed} null_flagged={null_flagged} not_computable={skipped}"
    )
    for result in results:
        detail = result["formula"] or result["growth_result"]
        print(f"  {result['period']} | spend={result['actual_spend'] or 'NULL'} | {detail}")
    print(f"[done] wrote {args.output}")


if __name__ == "__main__":
    main()
