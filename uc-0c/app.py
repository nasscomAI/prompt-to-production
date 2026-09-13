"""
UC-0C app.py — "Number That Looks Right".

Produces a per-ward per-category, per-period growth table from
../data/budget/ward_budget.csv. It never aggregates across wards or categories,
flags every null actual_spend row (with the reason from the notes column),
shows the formula used in every output row, and refuses to guess the growth type.
"""
import argparse
import csv
import re
import sys
from datetime import datetime

REQUIRED_COLUMNS = ["period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ["MoM", "YoY"]
AGGREGATION_PATTERN = re.compile(r"\b(?:all|every|any|total|aggregate|combined)\b", re.IGNORECASE)


def _format_number(value):
    """Render a float without trailing digits, e.g. 19.7 or 13.0."""
    if value == int(value):
        return f"{int(value)}"
    return f"{value:g}"


def _growth_text(growth):
    if growth is None:
        return ""
    sign = "+" if growth >= 0 else ""
    return f"{sign}{growth:.1f}%"


def is_aggregation_request(value):
    return value.strip().strip("*").lower() in ("", "all", "every", "any", "total", "combined", "aggregate") or bool(AGGREGATION_PATTERN.search(value))


def load_dataset(path):
    """Read CSV, validate columns, report null count and which rows.

    Returns (rows, null_rows) where null_rows is a list of dicts whose
    actual_spend is blank. Never aggregates: it only validates and reports.
    """
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}")
    if not rows:
        raise SystemExit(f"error: empty dataset at {path}")
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise SystemExit(f"error: missing required column(s): {', '.join(missing)}")
    null_rows = [r for r in rows if r["actual_spend"].strip() == ""]
    print(f"UC-0C load_dataset: {len(rows)} rows, "
          f"{len({r['ward'] for r in rows})} wards, "
          f"{len({r['category'] for r in rows})} categories.",
          file=sys.stderr)
    print(f"UC-0C load_dataset: {len(null_rows)} null actual_spend row(s) detected:",
          file=sys.stderr)
    for r in sorted(null_rows, key=lambda r: r["period"]):
        print(f"  - {r['period']}, {r['ward']}, {r['category']}: "
              f"{r['notes'].strip() or 'no reason given'}", file=sys.stderr)
    return rows, null_rows


def _parse_period(value):
    return datetime.strptime(value, "%Y-%m").date()


def _period_key(value):
    return _parse_period(value).replace(day=1)


def _compute_series(rows, ward, category, growth_type):
    """Helper for compute_growth: build the ordered per-period table.

    Returns a list of output rows (dicts) ready for the CSV writer.
    """
    values = {}
    for r in rows:
        values[_period_key(r["period"])] = r
    table = []
    ordered = sorted(values)
    for period in ordered:
        r = values[period]
        actual_raw = r["actual_spend"].strip()

        if growth_type == "MoM":
            prior_key = ordered[ordered.index(period) - 1] if ordered.index(period) > 0 else None
            prior_note = "no prior month for MoM"
        else:
            prior_key = period.replace(year=period.year - 1)
            prior_note = f"no prior-year period {prior_key.isoformat()} for YoY"
        prev = values.get(prior_key) if prior_key else None
        prev_raw = prev["actual_spend"].strip() if prev else ""

        if actual_raw == "":
            formula = f"FLAGGED — actual_spend is NULL; not computed ({r['notes'].strip() or 'no reason given'})"
            growth = None
        elif prev is None:
            formula = f"N/A — {prior_note} (dataset starts {ordered[0].isoformat()})"
            growth = None
        elif prev_raw == "":
            formula = (f"N/A — prior period actual_spend is NULL; "
                       f"not computed ({prev['notes'].strip() or 'no reason given'})")
            growth = None
        else:
            current = float(actual_raw)
            prior = float(prev_raw)
            growth = (current - prior) / prior * 100
            formula = (f"({_format_number(current)} - {_format_number(prior)}) "
                       f"/ {_format_number(prior)} * 100 = {_growth_text(growth)}")

        table.append({
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": actual_raw,
            "growth_type": growth_type,
            "formula": formula,
            "growth_pct": _growth_text(growth) if growth is not None else "",
            "notes": r["notes"],
        })
    return table


def compute_growth(rows, ward, category, growth_type):
    """Compute per-period growth for one ward + one category.

    Returns a per-period table (list of dicts) with the formula shown in every
    row. Raises SystemExit if ward/category are aggregation requests or are not
    exactly present in the dataset.
    """
    canonical = {"mom": "MoM", "m/m": "MoM", "yoy": "YoY", "y/y": "YoY"}
    requested = growth_type
    growth_type = canonical.get(requested.strip().lower())
    if growth_type is None:
        raise SystemExit(
            f"error: choose --growth-type MoM or YoY; refused guess of '{requested}'")
    if is_aggregation_request(ward):
        raise SystemExit(
            f"REFUSED: '{ward}' requests all-ward aggregation. "
            f"UC-0C outputs one ward at a time; pick one from: "
            f"{sorted({r['ward'] for r in rows})}")
    if is_aggregation_request(category):
        raise SystemExit(
            f"REFUSED: '{category}' requests cross-category aggregation. "
            f"UC-0C outputs one category at a time; pick one from: "
            f"{sorted({r['category'] for r in rows})}")
    wards = {r["ward"] for r in rows}
    categories = {r["category"] for r in rows}
    if ward not in wards:
        raise SystemExit(f"error: unknown ward '{ward}'. Choose one of: {sorted(wards)}")
    if category not in categories:
        raise SystemExit(f"error: unknown category '{category}'. Choose one of: {sorted(categories)}")
    scoped = [r for r in rows if r["ward"] == ward and r["category"] == category]
    return _compute_series(scoped, ward, category, growth_type)


def write_output(table, output_path):
    columns = ["period", "ward", "category", "budgeted_amount", "actual_spend",
               "growth_type", "formula", "growth_pct", "notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(table)
    print(f"UC-0C: wrote {len(table)} per-period rows to {output_path}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Per-ward per-category growth table (UC-0C). "
                    "Produces per-period growth for exactly one ward and one category.")
    parser.add_argument("--input", required=True,
                        help="path to ../data/budget/ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="single ward name from the dataset (aggregation is refused)")
    parser.add_argument("--category", required=True,
                        help="single category name from the dataset (aggregation is refused)")
    parser.add_argument("--growth-type", required=True,
                        choices=GROWTH_TYPES,
                        help="MoM or YoY. Required — never guessed.")
    parser.add_argument("--output", default="growth_output.csv",
                        help="output CSV path")
    args = parser.parse_args(argv)
    rows, null_rows = load_dataset(args.input)
    table = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(table, args.output)


if __name__ == "__main__":
    main()
