"""
UC-0C — Number That Looks Right
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.

Fixes applied over the naive baseline (see git history for the naive
Control-step run and its failures):
  1. Silent aggregation -> compute_growth REQUIRES one ward and one
                            category; there is no code path that sums
                            across wards or categories. Asking for a
                            citywide number is refused with an explicit
                            message, not silently honoured.
  2. Silent null skipping -> load_dataset reports every null row (period,
                            ward, category, reason) before any computation
                            runs, and null rows stay in the series as
                            explicit NULL entries in the output instead of
                            being dropped from the sum.
  3. Formula assumption  -> --growth-type is required with no default;
                            MoM and YoY are both supported, and every
                            output row shows the exact arithmetic used.

See agents.md for the enforcement rules this file implements and skills.md
for the two skills (load_dataset, compute_growth) this file defines.
"""
import argparse
import csv
import sys

VALID_GROWTH_TYPES = ("MoM", "YoY")


def load_dataset(input_path: str):
    """
    Read ward_budget.csv, validate columns, and report every null
    actual_spend row (period/ward/category/reason) before returning.
    Null rows are kept in the dataset with actual_spend=None -- never
    dropped, never coerced to 0.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or not required_cols.issubset(set(reader.fieldnames)):
                missing = required_cols - set(reader.fieldnames or [])
                raise ValueError(f"Input CSV is missing required column(s): {sorted(missing)}")
            raw_rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    dataset = []
    null_rows = []
    for row in raw_rows:
        spend_str = (row.get("actual_spend") or "").strip()
        actual_spend = float(spend_str) if spend_str else None
        parsed = {
            "period": row["period"].strip(),
            "ward": row["ward"].strip(),
            "category": row["category"].strip(),
            "budgeted_amount": float(row["budgeted_amount"]),
            "actual_spend": actual_spend,
            "notes": (row.get("notes") or "").strip(),
        }
        dataset.append(parsed)
        if actual_spend is None:
            null_rows.append(parsed)

    print(f"load_dataset: {len(dataset)} rows loaded from {input_path}")
    print(f"load_dataset: {len(null_rows)} row(s) have a NULL actual_spend:")
    for nr in null_rows:
        reason = nr["notes"] or "(no reason given in notes column)"
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} -> {reason}")

    return dataset


def _resolve_value(dataset_values, requested, field_name):
    """Exact match, then case-insensitive, then unambiguous substring.
    Never silently guesses among multiple candidates."""
    if requested in dataset_values:
        return requested
    ci_matches = [v for v in dataset_values if v.lower() == requested.lower()]
    if len(ci_matches) == 1:
        return ci_matches[0]
    sub_matches = [v for v in dataset_values if requested.lower() in v.lower()]
    if len(sub_matches) == 1:
        return sub_matches[0]
    valid = ", ".join(sorted(dataset_values))
    if len(sub_matches) > 1:
        raise ValueError(
            f"{field_name} '{requested}' is ambiguous -- matches multiple values: "
            f"{', '.join(sorted(sub_matches))}. Be more specific."
        )
    raise ValueError(f"{field_name} '{requested}' not found. Valid values are: {valid}")


def _shift_period(period: str, months_delta: int) -> str:
    year, month = (int(p) for p in period.split("-"))
    total = year * 12 + (month - 1) + months_delta
    new_year, new_month = divmod(total, 12)
    return f"{new_year:04d}-{new_month + 1:02d}"


def compute_growth(dataset, ward: str, category: str, growth_type: str):
    """
    Return a per-period growth table for exactly one ward + one category.
    Refuses (raises ValueError) rather than aggregating or guessing when
    ward, category, or growth_type is missing/invalid/ambiguous.
    """
    if not ward or not category:
        raise ValueError(
            "Refusing to compute growth without an explicit ward AND category. "
            "This program never aggregates across wards or categories -- "
            "pass --ward and --category to select exactly one series."
        )
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Refusing to guess a growth formula. --growth-type is required and "
            f"must be exactly one of: {', '.join(VALID_GROWTH_TYPES)}."
        )

    all_wards = {r["ward"] for r in dataset}
    all_categories = {r["category"] for r in dataset}
    resolved_ward = _resolve_value(all_wards, ward, "ward")
    resolved_category = _resolve_value(all_categories, category, "category")

    series = {
        r["period"]: r
        for r in dataset
        if r["ward"] == resolved_ward and r["category"] == resolved_category
    }
    if not series:
        raise ValueError(f"No rows found for ward='{resolved_ward}' category='{resolved_category}'.")

    months_delta = -1 if growth_type == "MoM" else -12
    label = "previous month" if growth_type == "MoM" else "same month, prior year"

    results = []
    for period in sorted(series):
        current = series[period]
        comparison_period = _shift_period(period, months_delta)
        comparison = series.get(comparison_period)

        row = {
            "ward": resolved_ward,
            "category": resolved_category,
            "period": period,
            "actual_spend": current["actual_spend"] if current["actual_spend"] is not None else "NULL",
            "growth_type": growth_type,
            "comparison_period": comparison_period,
            "growth_pct": "NULL",
            "formula": "",
            "null_reason": "",
        }

        if current["actual_spend"] is None:
            row["null_reason"] = (
                f"actual_spend for {period} is NULL ({current['notes'] or 'no reason given'}); "
                f"growth not computed."
            )
        elif comparison is None:
            row["null_reason"] = f"no {label} ({comparison_period}) exists in the dataset for this series."
        elif comparison["actual_spend"] is None:
            row["null_reason"] = (
                f"comparison period {comparison_period} actual_spend is NULL "
                f"({comparison['notes'] or 'no reason given'}); growth not computed."
            )
        else:
            prev_val = comparison["actual_spend"]
            curr_val = current["actual_spend"]
            if prev_val == 0:
                row["null_reason"] = f"comparison period {comparison_period} actual_spend is 0; growth undefined (division by zero)."
            else:
                growth_pct = round((curr_val - prev_val) / prev_val * 100, 1)
                row["growth_pct"] = growth_pct
                row["formula"] = f"({curr_val} - {prev_val}) / {prev_val} * 100 = {growth_pct}%"

        results.append(row)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    parser.add_argument("--ward", required=False, help="Exact (or unambiguous partial) ward name")
    parser.add_argument("--category", required=False, help="Exact (or unambiguous partial) category name")
    parser.add_argument("--growth-type", required=False, choices=list(VALID_GROWTH_TYPES),
                         help="MoM or YoY -- required, never defaulted")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    if not args.ward or not args.category or not args.growth_type:
        all_wards = sorted({r["ward"] for r in dataset})
        all_categories = sorted({r["category"] for r in dataset})
        print("\nRefusing to proceed: --ward, --category, and --growth-type are all required.")
        print("This tool never aggregates across wards/categories and never assumes a formula.")
        print(f"Valid wards: {all_wards}")
        print(f"Valid categories: {all_categories}")
        print(f"Valid growth types: {list(VALID_GROWTH_TYPES)}")
        sys.exit(2)

    try:
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print(f"\nRefused: {exc}")
        sys.exit(2)

    fieldnames = ["ward", "category", "period", "actual_spend", "growth_type",
                  "comparison_period", "growth_pct", "formula", "null_reason"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    null_count = sum(1 for r in results if r["growth_pct"] == "NULL")
    print(f"\nDone. {len(results)} periods for {args.ward} / {args.category} "
          f"({null_count} flagged NULL) -> {args.output}")


if __name__ == "__main__":
    main()
