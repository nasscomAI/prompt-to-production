"""
UC-0C app.py — Ward-budget growth calculator.

Per-ward per-category growth table; never a single aggregated number.
See agents.md / skills.md for the enforced rules.
"""
import argparse
import csv
import sys
from collections import OrderedDict

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH_TYPES = ("MoM", "YoY")
AGGREGATION_KEYWORDS = ("all", "any", "*", "total", "everything", "all wards", "all categories")


def load_dataset(input_path):
    """
    Read the ward-budget CSV, validate required columns, count nulls and
    report which rows have null actual_spend before returning.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ValueError("CSV appears to be empty — no header row found")
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(
                    "CSV is missing required column(s): {}. Found: {}".format(
                        ", ".join(missing), ", ".join(reader.fieldnames)
                    )
                )
            rows = []
            for line_no, raw in enumerate(reader, start=2):
                period = raw["period"].strip()
                ward = raw["ward"].strip()
                category = raw["category"].strip()
                actual_raw = raw["actual_spend"].strip()
                budgeted_raw = raw["budgeted_amount"].strip()
                budgeted = _parse_number(budgeted_raw, line_no, "budgeted_amount")
                if actual_raw == "":
                    actual = None
                else:
                    actual = _parse_number(actual_raw, line_no, "actual_spend")
                rows.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual,
                        "notes": raw["notes"].strip(),
                    }
                )
    except FileNotFoundError:
        raise FileNotFoundError("Input file not found: {}".format(input_path))
    except csv.Error as exc:
        raise ValueError("Could not parse CSV {}: {}".format(input_path, exc))

    null_rows = [r for r in rows if r["actual_spend"] is None]
    _report_nulls(null_rows)

    expected = 300
    if len(rows) != expected:
        print(
            "[warn] Expected {} data rows but found {} — continuing with what was loaded "
            "(nulls still flagged).".format(expected, len(rows)),
            file=sys.stderr,
        )
    else:
        print("Loaded {} rows. Null actual_spend count: {}".format(len(rows), len(null_rows)))
    return rows


def _parse_number(text, line_no, column):
    try:
        return float(text)
    except ValueError:
        raise ValueError(
            "Line {}: '{}' is not a valid number in column '{}'.".format(
                line_no, text, column
            )
        )


def _report_nulls(null_rows):
    print("Null actual_spend rows found before any computation:", file=sys.stderr)
    if not null_rows:
        print("  (none)", file=sys.stderr)
    for r in null_rows:
        reason = r["notes"] or "no reason given in notes"
        print("  {} | {} | {} | reason: {}".format(r["period"], r["ward"], r["category"], reason), file=sys.stderr)


def _period_to_prev(period, growth_type):
    year, month = period.split("-")
    year, month = int(year), int(month)
    if growth_type == "MoM":
        if month == 1:
            return "{:04d}-{:02d}".format(year - 1, 12)
        return "{:04d}-{:02d}".format(year, month - 1)
    # YoY
    return "{:04d}-{:02d}".format(year - 1, month)


def _refuse(ward, category):
    kw = set(AGGREGATION_KEYWORDS)
    messages = []
    for label, value in (("--ward", ward), ("--category", category)):
        if value is None or value.strip().lower() in kw:
            messages.append(
                "Cannot compute growth: {} must name exactly one ward/category. "
                "This tool never aggregates across wards or categories.".format(label)
            )
    if not ward.strip() or not category.strip():
        messages.extend(
            [
                "--ward and --category are required (per-ward per-category output only).",
                "Computing all wards or all categories in one table is REFUSED.",
            ]
        )
    return messages


def compute_growth(rows, ward, category, growth_type):
    """
    Return a per-period table for one ward + category with formula shown.
    """
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            "Unsupported --growth-type '{}'. Supported: {}. Refusing to guess a formula.".format(
                growth_type, ", ".join(SUPPORTED_GROWTH_TYPES)
            )
        )

    formula = (
        "MoM = (current_spend - previous_month_spend) / previous_month_spend x 100"
        if growth_type == "MoM"
        else "YoY = (current_spend - same_month_previous_year_spend) / same_month_previous_year_spend x 100"
    )

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        valid_wards = sorted({r["ward"] for r in rows})
        valid_categories = sorted({r["category"] for r in rows})
        detail = ""
        if ward not in valid_wards:
            detail += " No such ward. Valid wards: {}".format(", ".join(valid_wards))
        if category not in valid_categories:
            detail += " No such category. Valid categories: {}".format(", ".join(valid_categories))
        raise ValueError("No data found for ward='{}', category='{}'.{}".format(ward, category, detail))

    by_period = OrderedDict((r["period"], r) for r in sorted(filtered, key=lambda r: r["period"]))

    output = []
    for period, row in by_period.items():
        prev_period = _period_to_prev(period, growth_type)
        prev_row = by_period.get(prev_period)

        if row["actual_spend"] is None:
            output.append(
                {
                    "period": period,
                    "actual_spend": "",
                    "previous_period": prev_period,
                    "previous_spend": "",
                    "growth_pct": "",
                    "formula_used": formula,
                    "null_flag": "true",
                    "null_reason": row["notes"] or "no reason given in notes",
                }
            )
            continue

        if prev_row is None or prev_row["actual_spend"] is None:
            output.append(
                {
                    "period": period,
                    "actual_spend": "{:.1f}".format(row["actual_spend"]),
                    "previous_period": prev_period,
                    "previous_spend": "" if prev_row is None else "",
                    "growth_pct": "",
                    "formula_used": formula,
                    "null_flag": "true",
                    "null_reason": "no previous {} period available".format(growth_type) if prev_row is None else "previous period spend is null",
                }
            )
            continue

        diff = row["actual_spend"] - prev_row["actual_spend"]
        pct = (diff / prev_row["actual_spend"]) * 100.0
        output.append(
            {
                "period": period,
                "actual_spend": "{:.1f}".format(row["actual_spend"]),
                "previous_period": prev_period,
                "previous_spend": "{:.1f}".format(prev_row["actual_spend"]),
                "growth_pct": "{:+.1f}%".format(pct),
                "formula_used": formula,
                "null_flag": "false",
                "null_reason": "",
            }
        )
    return output


def write_output(output_path, table):
    columns = [
        "period",
        "actual_spend",
        "previous_period",
        "previous_spend",
        "growth_pct",
        "formula_used",
        "null_flag",
        "null_reason",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(table)
    print("Wrote {} rows to {}".format(len(table), output_path))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Per-ward per-category monthly growth table (never aggregated)."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exactly one category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=False,
                        help="One of {}. REQUIRED — never guessed.".format(", ".join(SUPPORTED_GROWTH_TYPES)))
    parser.add_argument("--output", default="growth_output.csv")
    args = parser.parse_args(argv)

    if args.growth_type is None:
        print(
            "REFUSED: --growth-type was not specified. Pass --growth-type MoM or "
            "--growth-type YoY — the formula is never guessed.",
            file=sys.stderr,
        )
        return 2

    refusals = _refuse(args.ward, args.category)
    if refusals:
        for msg in refusals:
            print("REFUSED: " + msg, file=sys.stderr)
        return 2

    rows = load_dataset(args.input)
    table = compute_growth(rows, args.ward.strip(), args.category.strip(), args.growth_type)
    write_output(args.output, table)
    print(
        "Growth type: {} | Ward: {} | Category: {} | {} rows output.".format(
            args.growth_type, args.ward, args.category, len(table)
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())