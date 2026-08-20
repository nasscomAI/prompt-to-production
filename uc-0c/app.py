"""
UC-0C — Number That Looks Right

Analyses ward budget data and computes per-ward, per-category growth.

Failure modes guarded against (from agents.md / README):
  * Wrong aggregation level -> per-ward per-category only; cross-ward or
    cross-category aggregation is refused outright.
  * Silent null handling     -> every null actual_spend row is reported with
    the reason from the notes column before any computation.
  * Formula assumption       -> --growth-type is mandatory; the exact formula
    used is printed on every output row; YoY is refused because the dataset
    (Jan-Dec 2024) has no prior-year baseline.
"""
import argparse
import csv
import os
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

ALLOWED_GROWTH_TYPES = {"MoM", "YoY"}


def _norm(s):
    """Case-insensitive compare with dash/space normalisation."""
    if s is None:
        return ""
    return re.sub(r"\s+", " ", s.lower().replace("–", "-").replace("—", "-")).strip()


def _to_float(value):
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_dataset(input_path):
    """Read CSV, validate columns, report null count and which rows are null."""
    if not os.path.exists(input_path):
        raise SystemExit(f"Input file not found: {input_path}")

    rows = []
    null_rows = []

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"CSV missing required columns: {', '.join(missing)}")

        for row in reader:
            period = str(row.get("period", "")).strip()
            ward = str(row.get("ward", "")).strip()
            category = str(row.get("category", "")).strip()
            budgeted = _to_float(row.get("budgeted_amount"))
            actual = _to_float(row.get("actual_spend"))
            notes = str(row.get("notes", "")).strip()

            if not period or not ward or not category:
                raise SystemExit(f"Invalid row: missing period/ward/category: {row}")

            if actual is None:
                null_rows.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "notes": notes or "actual_spend missing",
                })

            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted": budgeted,
                "actual": actual,
                "notes": notes,
            })

    return rows, null_rows


def _resolve_selection(rows, ward_arg, category_arg):
    """Return the exact ward/category strings present in the data (or None)."""
    wards = {_norm(r["ward"]): r["ward"] for r in rows}
    categories = {_norm(r["category"]): r["category"] for r in rows}

    ward = wards.get(_norm(ward_arg))
    category = categories.get(_norm(category_arg))
    return ward, category


def compute_growth(rows, ward, category, growth_type):
    """Per-period MoM table for a single ward + category, formula shown."""
    selected = [r for r in rows if r["ward"] == ward and r["category"] == category]
    selected.sort(key=lambda r: r["period"])

    out = []
    prev_actual = None
    for r in selected:
        cur = r["actual"]
        if cur is None:
            out.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "budgeted_amount": r["budgeted"],
                "actual_spend": "NULL",
                "previous_period_actual_spend": "" if prev_actual is None else f"{prev_actual:.1f}",
                "growth_type": growth_type,
                "growth_pct": "N/A",
                "formula": "N/A - actual_spend is null; growth not computed",
                "flag": "NULL_ACTUAL_SPEND",
                "notes": r["notes"] or "actual_spend missing",
            })
        elif prev_actual is None:
            out.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "budgeted_amount": r["budgeted"],
                "actual_spend": f"{cur:.1f}",
                "previous_period_actual_spend": "N/A",
                "growth_type": growth_type,
                "growth_pct": "N/A",
                "formula": "MoM = (current - previous) / previous * 100 - no previous month",
                "flag": "",
                "notes": "",
            })
        else:
            pct = (cur - prev_actual) / prev_actual * 100
            out.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "budgeted_amount": r["budgeted"],
                "actual_spend": f"{cur:.1f}",
                "previous_period_actual_spend": f"{prev_actual:.1f}",
                "growth_type": growth_type,
                "growth_pct": f"{pct:+.1f}%",
                "formula": "MoM = (current - previous) / previous * 100",
                "flag": "",
                "notes": "",
            })
        prev_actual = cur

    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget MoM Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", required=False, help="Category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM (YoY is refused)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Refusal: growth type is mandatory — never guess.
    if not args.growth_type:
        print("REFUSED: --growth-type is required. Refusing to guess between "
              "MoM and YoY.", file=sys.stderr)
        sys.exit(1)

    growth_type = args.growth_type.strip()
    if growth_type not in ALLOWED_GROWTH_TYPES:
        print(f"REFUSED: unknown growth-type '{growth_type}'. "
              f"Allowed values: {sorted(ALLOWED_GROWTH_TYPES)}.", file=sys.stderr)
        sys.exit(1)

    # Refusal: YoY cannot be computed from a single-year dataset.
    if growth_type == "YoY":
        print("REFUSED: YoY growth requires a prior-year baseline, but the dataset "
              "only covers Jan-Dec 2024. Use MoM instead.", file=sys.stderr)
        sys.exit(1)

    # Refusal: cross-ward / cross-category aggregation is never allowed.
    if not args.ward or not args.category:
        print("REFUSED: both --ward and --category are required. Aggregating "
              "across wards or categories is not permitted.", file=sys.stderr)
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows from {args.input}.")
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend row(s) - flagged before computing:")
        for nr in null_rows:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} "
                  f"| reason: {nr['notes']}")
    else:
        print("No null actual_spend rows found.")

    ward, category = _resolve_selection(rows, args.ward, args.category)
    if ward is None:
        raise SystemExit(f"Ward not found in data: {args.ward}")
    if category is None:
        raise SystemExit(f"Category not found in data: {args.category}")

    results = compute_growth(rows, ward, category, growth_type)

    columns = ["period", "ward", "category", "budgeted_amount", "actual_spend",
               "previous_period_actual_spend", "growth_type", "growth_pct",
               "formula", "flag", "notes"]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nComputed {growth_type} growth for {ward} / {category}:")
    for r in results:
        print(f"  {r['period']}: actual={r['actual_spend']:>6} "
              f"growth={r['growth_pct']:>8} {r['flag']}")
    print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()