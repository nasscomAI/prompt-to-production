"""
UC-0C — per-ward, per-category budget growth (MoM / YoY).

Operates strictly at the (ward, category) level. Never aggregates across wards or
categories, never fills null actual_spend with guesses, and never picks a growth
formula silently. Any such request (or a missing --growth-type) is refused.
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

FORMULAS = {
    "MoM": "(current - previous month) / previous month",
    "YoY": "(current - same period previous year) / same period previous year",
}

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth",
    "growth_formula",
    "growth_note",
    "null_flag",
    "null_reason",
]


def load_dataset(path):
    """Skill: load_dataset — reads CSV, validates columns, reports null count and which rows."""
    if not os.path.exists(path):
        raise FileNotFoundError("input file not found: {0}".format(path))
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("input file has no data rows: {0}".format(path))
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError("input file missing required columns: {0}".format(", ".join(missing)))

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    sys.stderr.write("Loaded {0} rows. Null actual_spend rows: {1}.\n".format(len(rows), len(null_rows)))
    for r in null_rows:
        sys.stderr.write(
            "  NULL {0} | {1} | {2} | notes: {3}\n".format(r["period"], r["ward"], r["category"], r["notes"])
        )
    return rows, null_rows


def _to_float(value):
    text = (value or "").strip()
    return None if text == "" else float(text)


def _previous_period(period, growth_type):
    year, month = period.split("-")
    if growth_type == "MoM":
        prev_month = int(month) - 1
        if prev_month < 1:
            return None
        return "{0}-{1:02d}".format(year, prev_month)
    prev_year = int(year) - 1
    return "{0}-{1}".format(prev_year, month)


def compute_growth(rows, ward, category, growth_type):
    """Skill: compute_growth — returns per-period growth table for one (ward, category)."""
    formula = FORMULAS[growth_type]
    filtered = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    by_period = {r["period"]: r for r in filtered}

    output = []
    for r in filtered:
        actual = _to_float(r.get("actual_spend"))
        if actual is None:
            output.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth": "",
                "growth_formula": "NULL - not computed (actual_spend missing)",
                "growth_note": "",
                "null_flag": "TRUE",
                "null_reason": (r.get("notes") or "").strip() or "no reason given",
            })
            continue

        prev_period = _previous_period(r["period"], growth_type)
        prev_row = by_period.get(prev_period) if prev_period else None
        prev = _to_float(prev_row.get("actual_spend")) if prev_row else None
        if prev is None:
            output.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": r["actual_spend"],
                "growth": "",
                "growth_formula": formula,
                "growth_note": "no previous {0} period available".format(growth_type),
                "null_flag": "",
                "null_reason": "",
            })
            continue

        growth = (actual - prev) / prev
        output.append({
            "period": r["period"],
            "ward": ward,
            "category": category,
            "actual_spend": r["actual_spend"],
            "growth": round(growth, 4),
            "growth_formula": formula,
            "growth_note": "",
            "null_flag": "",
            "null_reason": "",
        })
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Per-ward, per-category budget growth (MoM or YoY) from ward_budget.csv"
    )
    parser.add_argument("--input", default=os.path.join("..", "data", "budget", "ward_budget.csv"))
    parser.add_argument("--ward", help="Ward to analyze; omit to process every ward individually")
    parser.add_argument("--category", help="Category to analyze; omit to process every category individually")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", default="growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        sys.exit("REFUSE: --growth-type is required (MoM or YoY). Please specify it explicitly.")

    try:
        rows, _ = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        sys.exit("REFUSE: {0}".format(exc))

    valid_wards = sorted({r["ward"] for r in rows})
    valid_categories = sorted({r["category"] for r in rows})

    wards = [args.ward] if args.ward else valid_wards
    categories = [args.category] if args.category else valid_categories
    for w in wards:
        if w not in valid_wards:
            sys.exit("REFUSE: ward '{0}' not in dataset. Available: {1}".format(w, valid_wards))
    for c in categories:
        if c not in valid_categories:
            sys.exit("REFUSE: category '{0}' not in dataset. Available: {1}".format(c, valid_categories))

    output_rows = []
    for w in wards:
        for c in categories:
            output_rows.extend(compute_growth(rows, w, c, args.growth_type))

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)
    print("Wrote {0} rows ({1} wards x {2} categories x 12 periods) to {3}".format(
        len(output_rows), len(wards), len(categories), args.output
    ))


if __name__ == "__main__":
    main()
