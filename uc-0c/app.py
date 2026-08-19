"""
UC-0C — Number That Looks Right

Budget growth calculator for a SINGLE ward + category, as a per-period table.

Enforcement rules from agents.md mapped to code:
  1. never aggregate across wards or categories — refuse if asked (ward/category = "ALL")
  2. flag every null actual_spend row before computing, reporting the reason
  3. show the formula used in every output row alongside the result
  4. growth type must be given (MoM or YoY) — missing => refuse, never guess
  5. unknown ward/category => refuse, listing valid values

Standard library only — runs on Python 3.9+ with no dependencies.
"""
import argparse
import csv
import sys

ALLOWED_GROWTH_TYPES = ("MoM", "YoY")
REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

# README reference values — self-checked when this series is requested.
REFERENCE_CHECKS = [
    ("Ward 1 – Kasba", "Roads & Pothole Repair", "2024-07", 19.7, 33.1),
    ("Ward 1 – Kasba", "Roads & Pothole Repair", "2024-10", 13.1, -34.8),
]

OUTPUT_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes",
    "previous_period", "previous_actual_spend", "formula", "growth_pct", "flag",
]


def _to_float(value):
    text = str(value or "").strip()
    return float(text) if text else None


def _prev_period(period, growth_type):
    year, month = period.split("-")
    if growth_type == "MoM":
        if month == "01":
            return f"{int(year) - 1}-12"
        return f"{year}-{int(month) - 1:02d}"
    return f"{int(year) - 1}-{month}"


def load_dataset(path):
    """Read and validate the budget CSV; report null actual_spend rows."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            raise ValueError(f"Dataset missing required columns: {', '.join(missing)}")
        rows = list(reader)

    null_rows = [
        (r["period"], r["ward"], r["category"], (r.get("notes") or "").strip())
        for r in rows if _to_float(r.get("actual_spend")) is None
    ]
    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Per-period growth table for one ward + one category, formula shown."""
    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError(f"Unknown growth type '{growth_type}' — must be MoM or YoY")
    if ward.strip().lower() == "all" or category.strip().lower() == "all":
        raise ValueError(
            "Refused: aggregation across wards/categories is not permitted. "
            "Pass a single ward and a single category."
        )

    series = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not series:
        wards = sorted({r["ward"] for r in rows})
        categories = sorted({r["category"] for r in rows})
        raise ValueError(
            f"Refused: no data for ward='{ward}', category='{category}'. "
            f"Valid wards: {wards}. Valid categories: {categories}."
        )

    by_period = {r["period"]: r for r in series}
    out = []

    for period in sorted(by_period):
        row = by_period[period]
        actual = _to_float(row.get("actual_spend"))
        budgeted = _to_float(row.get("budgeted_amount"))
        notes = (row.get("notes") or "").strip()

        entry = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": f"{budgeted:.1f}" if budgeted is not None else "",
            "actual_spend": f"{actual:.1f}" if actual is not None else "",
            "notes": notes,
            "previous_period": "",
            "previous_actual_spend": "",
            "formula": "",
            "growth_pct": "",
            "flag": "",
        }

        if actual is None:
            entry["flag"] = "NULL_SPEND"
            entry["formula"] = f"{growth_type}: not computed — actual_spend is null"
            out.append(entry)
            continue

        base_period = _prev_period(period, growth_type)
        base = by_period.get(base_period)
        if base is None:
            entry["flag"] = "NO_BASE_PERIOD"
            entry["formula"] = f"{growth_type}: no base-period row for {base_period}"
            out.append(entry)
            continue

        base_actual = _to_float(base.get("actual_spend"))
        entry["previous_period"] = base_period
        if base_actual is None:
            entry["flag"] = "NULL_BASE_SPEND"
            entry["formula"] = f"{growth_type}: base period {base_period} actual_spend is null"
            out.append(entry)
            continue

        growth = (actual - base_actual) / base_actual * 100
        entry["previous_actual_spend"] = f"{base_actual:.1f}"
        entry["formula"] = f"{growth_type}: ({actual:.1f} - {base_actual:.1f}) / {base_actual:.1f} * 100"
        entry["growth_pct"] = f"{growth:.1f}"
        out.append(entry)

    return out


def check_reference(out_rows, ward, category):
    """Self-check against README reference values for the Kasba Roads series."""
    if (ward, category) != REFERENCE_CHECKS[0][:2]:
        return
    by_period = {r["period"]: r for r in out_rows}
    print("Reference check (README):")
    for _ward, _category, period, exp_actual, exp_growth in REFERENCE_CHECKS:
        row = by_period.get(period)
        if not row:
            print(f"  {period}: row missing")
            continue
        ok = row["actual_spend"] == f"{exp_actual:.1f}" and row["growth_pct"] == f"{exp_growth:.1f}"
        print(f"  {period}: actual={row['actual_spend']}, growth={row['growth_pct']}% "
              f"{'OK' if ok else f'EXPECTED {exp_actual} / {exp_growth}%'}")


def write_output(path, out_rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(out_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward (refusal: aggregation not permitted)")
    parser.add_argument("--category", required=True, help="Single category (refusal: aggregation not permitted)")
    parser.add_argument("--growth-type", required=True, choices=ALLOWED_GROWTH_TYPES,
                        help="Refusal: growth type must be given, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print("Null actual_spend rows (flagged before computing):")
    for period, ward, category, notes in null_rows:
        print(f"  {period} | {ward} | {category} | {notes or '(no reason given)'}")

    try:
        out = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print(f"Refused: {exc}")
        sys.exit(1)

    write_output(args.output, out)

    computed = sum(1 for r in out if r["growth_pct"] != "")
    flagged = sum(1 for r in out if r["flag"] != "")
    print(f"Rows: {len(out)} | growth computed: {computed} | flagged (not computed): {flagged}")
    check_reference(out, args.ward, args.category)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
