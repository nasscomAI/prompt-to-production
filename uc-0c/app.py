"""
UC-0C — Number That Looks Right
Per-ward per-category budget growth calculator for ward_budget.csv.

Run:
  python app.py \
    --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" \
    --category "Roads & Pothole Repair" \
    --growth-type MoM \
    --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
ALLOWED_GROWTH_TYPES = ("MoM", "YoY")
OUTPUT_FIELDS = ["ward", "category", "period", "previous_period", "previous_value",
                 "current_value", "growth_percent", "formula", "flag", "null_reason"]


def load_dataset(input_path):
    """
    Read and validate the budget CSV. Reports null actual_spend rows (count and
    exact rows with the reason from the notes column) before returning.
    Refuses if required columns are missing or the file cannot be read.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("file has no header row")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError("missing required column(s): " + ", ".join(sorted(missing)))
            rows = [dict(r) for r in reader]
    except OSError as exc:
        raise ValueError("cannot read input file: %s" % exc) from exc

    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    print("Loaded %d rows." % len(rows))
    print("Null actual_spend rows: %d" % len(null_rows))
    for r in null_rows:
        print("  NULL: %s | %s | %s | reason: %s" % (r["period"], r["ward"], r["category"], r["notes"] or "none given"))
    return rows


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_growth(rows, ward, category, growth_type):
    """
    Per-period growth table for one ward + one category only. Never aggregates
    across wards or categories, never guesses missing values, and shows the
    formula used alongside every computed result.
    """
    if not ward or not category:
        raise ValueError("Refusing: aggregation across wards/categories is not permitted. Provide --ward AND --category.")
    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError("Refusing: growth-type '%s' is unknown. Choose from %s." % (growth_type, ", ".join(ALLOWED_GROWTH_TYPES)))

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError("Refusing: no rows found for ward='%s' category='%s'. Only per-ward per-category output is permitted." % (ward, category))

    filtered.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in filtered}

    def previous_row(row):
        if growth_type == "MoM":
            idx = filtered.index(row)
            return filtered[idx - 1] if idx > 0 else None
        year, month = row["period"].split("-")
        return by_period.get("%04d-%s" % (int(year) - 1, month))

    results = []
    for row in filtered:
        prev = previous_row(row)
        prev_value = _to_float(prev["actual_spend"]) if prev is not None else None
        curr_value = _to_float(row["actual_spend"])
        out = {
            "ward": row["ward"],
            "category": row["category"],
            "period": row["period"],
            "previous_period": prev["period"] if prev is not None else "",
            "previous_value": "" if prev_value is None else prev_value,
            "current_value": "" if curr_value is None else curr_value,
            "growth_percent": "",
            "formula": "",
            "flag": "",
            "null_reason": "",
        }
        if not row["actual_spend"].strip():
            out["flag"] = "NULL_SKIPPED"
            out["null_reason"] = row["notes"] or "no reason given"
        elif prev_value is None:
            out["flag"] = "NO_PREVIOUS_PERIOD"
        else:
            pct = (curr_value - prev_value) / prev_value * 100
            out["growth_percent"] = round(pct, 1)
            out["formula"] = "%s Growth = (%s - %s) / %s * 100" % (growth_type, curr_value, prev_value, prev_value)
        results.append(out)
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C — per-ward per-category budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", default=None, help="Category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", default=None, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if args.growth_type is None:
        print("Refusing: --growth-type not specified. Required: MoM or YoY.", file=sys.stderr)
        sys.exit(1)
    if not args.ward or not args.category:
        print("Refusing: aggregation across wards/categories is not permitted. Provide --ward AND --category.", file=sys.stderr)
        sys.exit(1)

    try:
        rows = load_dataset(args.input)
    except ValueError as exc:
        print("Refusing: %s" % exc, file=sys.stderr)
        sys.exit(1)

    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print("Refusing: %s" % exc, file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)
    print("Done. Results written to %s" % args.output)


if __name__ == "__main__":
    main()
