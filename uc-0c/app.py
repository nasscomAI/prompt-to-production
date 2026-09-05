"""
UC-0C app.py — Number That Looks Right
Computes per-ward per-category growth from the ward budget CSV.

Implements the rules from agents.md:
  - never aggregate across wards or categories (refuse all-ward queries)
  - flag every null actual_spend row with its reason from the notes column
  - show the formula on every output row
  - refuse if --growth-type is not specified; never guess the formula
"""
import argparse
import csv
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ["MoM", "YoY"]


def load_dataset(input_path: str) -> list:
    """
    Reads the ward budget CSV, validates columns, and reports null count and
    which rows are null before returning.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("Dataset is empty")

    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    null_rows = [r for r in rows if not (r["actual_spend"] or "").strip()]
    print(
        f"Loaded {len(rows)} rows. Found {len(null_rows)} null actual_spend rows:"
    )
    for r in null_rows:
        reason = (r["notes"] or "").strip() or "no reason provided"
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | {reason}")

    return rows


def _normalise(name: str) -> str:
    """Normalise dashes and whitespace so input matching is robust."""
    return re.sub(r"\s+", " ", name.replace("\u2013", "-").replace("\u2014", "-")).strip()


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes a ward, category, and growth type, and returns a per-period table
    with the formula shown on every row. Null rows are flagged, never computed.
    """
    ward_n = _normalise(ward)
    category_n = _normalise(category)

    scoped = [
        r for r in rows
        if _normalise(r["ward"]) == ward_n and _normalise(r["category"]) == category_n
    ]
    if not scoped:
        raise ValueError(
            f"No data for ward '{ward}' + category '{category}'. "
            "Refusing to aggregate across wards or categories."
        )

    scoped.sort(key=lambda r: r["period"])

    output = []
    n = len(scoped)
    for idx, row in enumerate(scoped):
        period = row["period"]
        budgeted = float(row["budgeted_amount"]) if (row["budgeted_amount"] or "").strip() else None
        actual_raw = (row["actual_spend"] or "").strip()
        notes = (row["notes"] or "").strip()

        # Null row: flag, never compute
        if not actual_raw:
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": None,
                "formula": f"{growth_type}: N/A — skipped (null actual_spend)",
                "growth_value": None,
                "flag": f"NULL - {notes or 'no reason provided'}",
            })
            continue

        actual = float(actual_raw)

        # Previous period value for the growth base
        prev_actual = None
        if idx > 0:
            prev_raw = (scoped[idx - 1]["actual_spend"] or "").strip()
            if prev_raw:
                prev_actual = float(prev_raw)

        growth_value = None
        if growth_type == "MoM":
            if prev_actual is None:
                formula = "MoM: N/A — no previous month in scope"
            elif prev_actual == 0:
                formula = "MoM: N/A — previous month actual_spend is zero"
            else:
                growth_value = round(((actual - prev_actual) / prev_actual) * 100, 1)
                formula = f"MoM: (({actual:g} - {prev_actual:g}) / {prev_actual:g}) * 100"
        elif growth_type == "YoY":
            prev_year = _find_prev_year(scoped, period)
            if prev_year is None:
                formula = "YoY: N/A — prior-year data not present in dataset"
            elif prev_year == 0:
                formula = "YoY: N/A — prior-year actual_spend is zero"
            else:
                growth_value = round(((actual - prev_year) / prev_year) * 100, 1)
                formula = f"YoY: (({actual:g} - {prev_year:g}) / {prev_year:g}) * 100"
        else:
            raise ValueError(
                f"Unknown growth type '{growth_type}'. Must be one of {VALID_GROWTH_TYPES}."
            )

        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "formula": formula,
            "growth_value": growth_value,
            "flag": "",
        })

    return output


def _find_prev_year(scoped: list, period: str):
    """Returns the actual_spend for the same month in the prior year, if present."""
    year, month = period.split("-")
    prev_key = f"{int(year) - 1}-{month}"
    for row in scoped:
        if row["period"] == prev_key and (row["actual_spend"] or "").strip():
            return float(row["actual_spend"])
    return None


def _write_output(output_path: str, table: list):
    fields = ["period", "ward", "category", "budgeted_amount", "actual_spend", "formula", "growth_value", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in table:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, default=None, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, default=None, choices=VALID_GROWTH_TYPES, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        raise SystemExit("REFUSED: --growth-type is required (MoM or YoY). I will not guess the formula.")
    if not args.ward or not args.category:
        raise SystemExit("REFUSED: --ward and --category are required. All-ward / all-category aggregation is not permitted.")

    rows = load_dataset(args.input)
    table = compute_growth(rows, args.ward, args.category, args.growth_type)
    _write_output(args.output, table)

    print(f"Done. Growth table written to {args.output} ({len(table)} rows)")


if __name__ == "__main__":
    main()