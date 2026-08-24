"""
UC-0C app.py

A deterministic CLI that computes month-over-month (MoM) or year-over-year
(YoY) spend growth for exactly one ward+category combination from the
municipal ward budget CSV. Pure standard-library arithmetic — no
aggregation across wards/categories, no silent null handling, no
model calls. See agents.md / skills.md / README.md for the contract this
implements.
"""

import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ("MoM", "YoY")


class AppError(Exception):
    """Raised whenever the agent must refuse rather than proceed."""


# ---------------------------------------------------------------------------
# load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path):
    """
    Reads the ward budget CSV, validates its structure, and reports every
    null actual_spend row (with its notes reason) before any computation
    happens.

    Returns a dict:
        {
            "records": [ {period, ward, category, budgeted_amount (float),
                           actual_spend (float or None), notes (str)}, ... ],
            "null_report": [ {period, ward, category, reason}, ... ],
            "total_rows": int,
            "null_count": int,
        }
    """
    if not os.path.isfile(file_path):
        raise AppError(f"File not found: '{file_path}'. Cannot load dataset.")

    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            raise AppError(
                "Dataset is missing required column(s): " + ", ".join(missing)
            )

        records = []
        null_report = []
        for row_num, row in enumerate(reader, start=2):  # header is line 1
            period = (row.get("period") or "").strip()
            ward = (row.get("ward") or "").strip()
            category = (row.get("category") or "").strip()
            notes = (row.get("notes") or "").strip()
            budgeted_raw = (row.get("budgeted_amount") or "").strip()
            actual_raw = (row.get("actual_spend") or "").strip()

            row_id = f"period={period!r}, ward={ward!r}, category={category!r} (CSV line {row_num})"

            # budgeted_amount must always be numeric.
            try:
                budgeted_amount = float(budgeted_raw)
            except ValueError:
                raise AppError(
                    f"Non-numeric budgeted_amount for row {row_id}: {budgeted_raw!r}"
                )

            # actual_spend must be numeric or blank.
            if actual_raw == "":
                if notes == "":
                    raise AppError(
                        f"Data-integrity failure for row {row_id}: actual_spend is "
                        "blank and notes is also blank, so the null cannot be "
                        "explained. Refusing to report an unexplained gap."
                    )
                actual_spend = None
                null_report.append(
                    {"period": period, "ward": ward, "category": category, "reason": notes}
                )
            else:
                try:
                    actual_spend = float(actual_raw)
                except ValueError:
                    raise AppError(
                        f"Malformed actual_spend for row {row_id}: {actual_raw!r} "
                        "is neither numeric nor blank."
                    )

            records.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budgeted_amount,
                    "actual_spend": actual_spend,
                    "notes": notes,
                }
            )

    return {
        "records": records,
        "null_report": null_report,
        "total_rows": len(records),
        "null_count": len(null_report),
    }


# ---------------------------------------------------------------------------
# compute_growth
# ---------------------------------------------------------------------------

def _period_key(period):
    """'YYYY-MM' -> (year:int, month:int) for arithmetic on periods."""
    year_s, month_s = period.split("-")
    return int(year_s), int(month_s)


def _shift_month(period, months_back):
    year, month = _period_key(period)
    total = year * 12 + (month - 1) - months_back
    new_year, new_month0 = divmod(total, 12)
    return f"{new_year:04d}-{new_month0 + 1:02d}"


def compute_growth(dataset, ward, category, growth_type):
    """
    Computes MoM or YoY growth, period by period, for exactly one
    ward+category pair, using only the validated output of load_dataset.

    Returns a list of per-period dict rows with keys: period, actual_spend,
    budgeted_amount, comparison_period, comparison_actual_spend, growth_pct,
    formula, flag.
    """
    # Refuse anything but a single scalar ward/category value.
    for label, value in (("ward", ward), ("category", category)):
        if not isinstance(value, str) or value.strip() == "":
            raise AppError(
                f"compute_growth requires a single {label} value; refusing to "
                "guess or aggregate across multiple values."
            )
        if value.strip().lower() in ("all", "*"):
            raise AppError(
                f"Refusing: '{value}' requests aggregation across every {label}. "
                "This skill only ever accepts a single ward+category pair."
            )

    records = dataset["records"]

    valid_wards = sorted({r["ward"] for r in records})
    valid_categories = sorted({r["category"] for r in records})

    if ward not in valid_wards:
        raise AppError(
            f"Ward '{ward}' not found in dataset. Valid ward values: "
            + ", ".join(valid_wards)
        )
    if category not in valid_categories:
        raise AppError(
            f"Category '{category}' not found in dataset. Valid category values: "
            + ", ".join(valid_categories)
        )

    if growth_type is None or growth_type not in VALID_GROWTH_TYPES:
        raise AppError(
            "growth_type must be specified explicitly as one of: "
            + ", ".join(VALID_GROWTH_TYPES) + ". Refusing to default."
        )

    # Index rows for this exact ward+category pair, by period.
    subset = {
        r["period"]: r for r in records if r["ward"] == ward and r["category"] == category
    }

    if not subset:
        # Should be unreachable given the ward/category checks above, but
        # guard against a dataset where the pair simply never co-occurs.
        raise AppError(
            f"No rows found for ward '{ward}' and category '{category}' combined."
        )

    months_back = 1 if growth_type == "MoM" else 12

    output_rows = []
    for period in sorted(subset.keys(), key=_period_key):
        target = subset[period]
        comparison_period = _shift_month(period, months_back)
        baseline = subset.get(comparison_period)

        row = {
            "period": period,
            "actual_spend": target["actual_spend"],
            "budgeted_amount": target["budgeted_amount"],
            "comparison_period": comparison_period,
            "comparison_actual_spend": None,
            "growth_pct": None,
            "formula": "",
            "flag": "",
        }

        if baseline is None:
            # No comparison period exists in the dataset at all.
            if growth_type == "YoY":
                row["growth_pct"] = "N/A — no prior-year data available"
            else:
                # MoM with no prior month present in the dataset (e.g. the
                # very first period, 2024-01, has no 2023-12 row to compare).
                row["growth_pct"] = "N/A — no comparison period available"
            output_rows.append(row)
            continue

        row["comparison_actual_spend"] = baseline["actual_spend"]

        # Null checks: target first, then baseline — both must be flagged
        # with their own notes reason wherever they occur.
        if target["actual_spend"] is None:
            row["growth_pct"] = "N/A — null data"
            row["flag"] = target["notes"]
        elif baseline["actual_spend"] is None:
            row["growth_pct"] = "N/A — null data"
            row["flag"] = baseline["notes"]
        else:
            actual = target["actual_spend"]
            base = baseline["actual_spend"]
            if base == 0:
                row["growth_pct"] = "N/A — baseline is zero"
            else:
                growth = (actual - base) / base * 100
                sign = "+" if growth >= 0 else "-"
                row["growth_pct"] = f"{growth:+.2f}%"
                row["formula"] = (
                    f"({actual} - {base}) / {base} * 100 = {sign}{abs(growth):.2f}%"
                )

        output_rows.append(row)

    return output_rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compute MoM or YoY spend growth for one ward+category pair."
    )
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV.")
    parser.add_argument("--ward", required=True, help="Exact ward name to analyze.")
    parser.add_argument("--category", required=True, help="Exact category name to analyze.")
    parser.add_argument(
        "--growth-type",
        required=False,
        default=None,
        choices=None,  # validated manually so we control the refusal message/order
        help="Must be exactly 'MoM' or 'YoY'. Never defaulted.",
    )
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv to.")
    return parser.parse_args(argv)


OUTPUT_FIELDS = [
    "period",
    "actual_spend",
    "budgeted_amount",
    "comparison_period",
    "comparison_actual_spend",
    "growth_pct",
    "formula",
    "flag",
]


def _fmt(value):
    return "" if value is None else value


def write_output(rows, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _fmt(row.get(k)) for k in OUTPUT_FIELDS})


def main(argv=None):
    args = parse_args(argv)

    # --growth-type is validated before any data is read or processed, per
    # agents.md: "refuse before reading or processing any data."
    if args.growth_type is None or args.growth_type not in VALID_GROWTH_TYPES:
        print(
            "Error: --growth-type must be specified explicitly as one of: "
            + ", ".join(VALID_GROWTH_TYPES) + ". Never defaulted. Exiting without "
            "producing output.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Guard against any wildcard/"all"/list value slipping through the CLI
    # before we even touch the dataset.
    for label, value in (("--ward", args.ward), ("--category", args.category)):
        if "," in value or value.strip().lower() in ("all", "*"):
            print(
                f"Error: {label} must be a single exact value; refusing request "
                f"that implies cross-ward/cross-category aggregation ({value!r}).",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        dataset = load_dataset(args.input)
        rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except AppError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    write_output(rows, args.output)
    print(
        f"Wrote {len(rows)} row(s) for ward={args.ward!r}, category={args.category!r}, "
        f"growth_type={args.growth_type} to {args.output}"
    )
    if dataset["null_count"]:
        print(f"Note: dataset contains {dataset['null_count']} null actual_spend row(s) overall:")
        for entry in dataset["null_report"]:
            print(
                f"  - {entry['period']} | {entry['ward']} | {entry['category']}: {entry['reason']}"
            )


if __name__ == "__main__":
    main()
