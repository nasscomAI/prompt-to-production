"""
UC-0C — Per-ward, per-category budget growth calculator.

load_dataset reads and validates the budget CSV and reports all null
actual_spend rows before any computation. compute_growth produces a
per-period table for exactly one ward-and-category pair using only the
explicitly requested growth type, showing the formula in every row.
Follows the agents.md enforcement rules and the skills.md error contracts.
"""
import argparse
import csv
import io
from datetime import datetime
import os
import sys

REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
]

SUPPORTED_GROWTH_TYPES = ("MoM", "YoY")

AGGREGATION_MARKERS = ("all", "*", "all wards", "all categories", "all wards and categories")


def _parse_float(value):
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return float(cleaned)


def load_dataset(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "Load refused: input file does not exist: {}".format(path))
    try:
        with io.open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            header = reader.fieldnames or []
            raw_rows = list(reader)
    except OSError as exc:
        raise OSError(
            "Load refused: cannot read {}: {}".format(path, exc))
    except csv.Error as exc:
        raise ValueError(
            "Load refused: malformed CSV in {}: {}".format(path, exc))

    missing_columns = [column for column in REQUIRED_COLUMNS
                       if column not in header]
    if missing_columns:
        raise ValueError(
            "Load refused: missing required column(s): {}. "
            "No data returned.".format(", ".join(missing_columns)))

    rows = []
    for index, raw in enumerate(raw_rows, start=2):
        try:
            period = (raw.get("period") or "").strip()
            datetime.strptime(period, "%Y-%m")
            ward = (raw.get("ward") or "").strip()
            category = (raw.get("category") or "").strip()
            budgeted_amount = float((raw.get("budgeted_amount") or "").strip())
            actual_spend = _parse_float(raw.get("actual_spend"))
            notes = (raw.get("notes") or "").strip()
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "Load refused: row {} has invalid values ({}). "
                "No data returned.".format(index, exc))
        if not ward or not category:
            raise ValueError(
                "Load refused: row {} has a blank ward or category. "
                "No data returned.".format(index))
        if actual_spend is None and not notes:
            raise ValueError(
                "Load refused: row {} has a null actual_spend with no "
                "explanation in notes; null reason cannot be resolved. "
                "No data returned.".format(index))
        rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted_amount,
            "actual_spend": actual_spend,
            "notes": notes,
        })

    null_rows = [row for row in rows if row["actual_spend"] is None]
    null_report = {
        "count": len(null_rows),
        "rows": [{
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "reason": row["notes"],
        } for row in null_rows],
    }
    return rows, null_report


def _period_key(period):
    parsed = datetime.strptime(period, "%Y-%m")
    return (parsed.year, parsed.month)


def _previous_period(period, growth_type):
    parsed = datetime.strptime(period, "%Y-%m")
    if growth_type == "MoM":
        year = parsed.year if parsed.month > 1 else parsed.year - 1
        month = parsed.month - 1 if parsed.month > 1 else 12
    else:
        year = parsed.year - 1
        month = parsed.month
    return "{:04d}-{:02d}".format(year, month)


def _formula_string(growth_type):
    if growth_type == "MoM":
        return "MoM = (current - previous) / previous * 100"
    return "YoY = (current - previous year same month) / previous * 100"


def compute_growth(rows, ward, category, growth_type, output_path):
    if not ward or not category:
        raise ValueError(
            "Compute refused: ward and category must both be specified; "
            "never aggregate across wards or categories.")
    ward_lower = ward.strip().lower()
    category_lower = category.strip().lower()
    if ward_lower in AGGREGATION_MARKERS or category_lower in AGGREGATION_MARKERS:
        raise ValueError(
            "Compute refused: aggregation request detected ({} / {}). "
            "Never aggregate across wards or categories.".format(ward, category))
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            "Compute refused: growth type '{}' is missing or not supported. "
            "Specify one of {} explicitly; never guess.".format(
                growth_type, ", ".join(SUPPORTED_GROWTH_TYPES)))

    known_wards = {row["ward"] for row in rows}
    known_categories = {row["category"] for row in rows}
    if ward not in known_wards:
        raise ValueError(
            "Compute refused: ward '{}' not found in the dataset. "
            "Known wards: {}.".format(ward, ", ".join(sorted(known_wards))))
    if category not in known_categories:
        raise ValueError(
            "Compute refused: category '{}' not found in the dataset. "
            "Known categories: {}.".format(category, ", ".join(sorted(known_categories))))

    series = [row for row in rows
              if row["ward"] == ward and row["category"] == category]
    series.sort(key=lambda row: _period_key(row["period"]))

    period_values = {row["period"]: row for row in series}

    output_rows = []
    for row in series:
        period = row["period"]
        reason = ""
        status = "computed"
        growth_pct = ""
        if row["actual_spend"] is None:
            status = "not computed"
            reason = row["notes"]
        else:
            prev_period = _previous_period(period, growth_type)
            prev_row = period_values.get(prev_period)
            if prev_row is None:
                status = "not computed"
                reason = "no {} data before {} in dataset".format(
                    "previous month" if growth_type == "MoM"
                    else "previous year same month",
                    period)
            elif prev_row["actual_spend"] is None:
                status = "not computed"
                reason = "previous period {} has null actual_spend: {}".format(
                    prev_period, prev_row["notes"])
            else:
                if prev_row["actual_spend"] == 0:
                    status = "not computed"
                    reason = "previous period {} actual_spend is zero; " \
                             "division undefined".format(prev_period)
                else:
                    growth_pct = round(
                        (row["actual_spend"] - prev_row["actual_spend"])
                        / prev_row["actual_spend"] * 100.0, 1)
                    status = "computed"
        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": ""
            if row["actual_spend"] is None else str(row["actual_spend"]),
            "growth_type": growth_type,
            "formula": _formula_string(growth_type),
            "growth_pct": str(growth_pct) if growth_pct != "" else "",
            "status": status,
            "notes": reason if reason else row["notes"],
        })

    header = ["period", "ward", "category", "actual_spend",
              "growth_type", "formula", "growth_pct", "status", "notes"]
    try:
        with io.open(output_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            writer.writeheader()
            writer.writerows(output_rows)
    except OSError as exc:
        raise OSError(
            "Compute refused: cannot write output {}: {}".format(
                output_path, exc))

    if not output_rows:
        raise ValueError(
            "Compute refused: no rows produced for {} / {}. "
            "No output written.".format(ward, category))
    return output_rows


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C per-ward, per-category budget growth calculator.")
    parser.add_argument("--input", required=True,
                        help="Path to the budget CSV.")
    parser.add_argument("--ward", required=True,
                        help="Ward to compute growth for (single ward).")
    parser.add_argument("--category", required=True,
                        help="Category to compute growth for (single category).")
    parser.add_argument("--growth-type", required=True, dest="growth_type",
                        help="Growth formula: MoM or YoY. Must be explicit.")
    parser.add_argument("--output", required=True,
                        help="Path to the per-ward per-category output CSV.")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)

    print("Null report: {} null actual_spend row(s) before computing:".format(
        null_report["count"]))
    for entry in null_report["rows"]:
        print("  {} | {} | {} | {}".format(
            entry["period"], entry["ward"], entry["category"], entry["reason"]))

    compute_growth(
        rows, args.ward, args.category, args.growth_type, args.output)
    print("Wrote per-ward per-category growth table to {} for '{}' / "
          "'{}' using {}".format(args.output, args.ward, args.category,
                                 args.growth_type))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)