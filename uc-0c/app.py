"""UC-0C app.py — deterministic ward/category growth analyzer. No aggregation."""
import argparse
import csv
import sys


def load_dataset(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing columns: %s" % sorted(missing))
        rows = []
        for r in reader:
            raw = (r.get("actual_spend") or "").strip()
            try:
                spend = float(raw) if raw != "" else None
            except ValueError:
                spend = None
            rows.append({
                "period": (r.get("period") or "").strip(),
                "ward": r.get("ward") or "",
                "category": r.get("category") or "",
                "actual_spend": spend,
                "notes": (r.get("notes") or "").strip(),
            })
    return rows


def compute_growth(rows, ward, category, growth_type):
    if not ward:
        raise ValueError("REFUSE: --ward is missing. Provide exact ward, e.g. 'Ward 1 - Kasba'.")
    if not category:
        raise ValueError("REFUSE: --category is missing. Provide exact category.")
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("REFUSE: --growth-type is missing or invalid. Specify MoM or YoY explicitly.")
    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not subset:
        raise ValueError("REFUSE: no rows for ward=%r category=%r." % (ward, category))
    subset.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in subset}
    out = []
    for i, r in enumerate(subset):
        prev = None
        if growth_type == "MoM" and i > 0:
            prev = subset[i - 1]
        elif growth_type == "YoY":
            y, m = r["period"].split("-")
            prev = by_period.get("%d-%s" % (int(y) - 1, m))
        curr_spend = r["actual_spend"]
        prev_spend = prev["actual_spend"] if prev else None
        if curr_spend is None:
            out.append({
                "period": r["period"], "ward": ward, "category": category,
                "actual_spend": "", "growth_pct": "",
                "formula": "n/a (current actual_spend is null)",
                "status": "NULL flagged: %s" % (r["notes"] or "no reason given"),
            })
        elif prev is None:
            reason = "first period, no prior %s value" % growth_type
            if growth_type == "YoY":
                reason = "no prior-year data for YoY"
            out.append({
                "period": r["period"], "ward": ward, "category": category,
                "actual_spend": str(curr_spend), "growth_pct": "",
                "formula": "n/a (%s)" % reason,
                "status": "n/a: %s" % reason,
            })
        elif prev_spend is None:
            out.append({
                "period": r["period"], "ward": ward, "category": category,
                "actual_spend": str(curr_spend), "growth_pct": "",
                "formula": "n/a (previous %s actual_spend is null)" % prev["period"],
                "status": "NULL flagged: previous %s null (%s)" % (
                    prev["period"], prev["notes"] or "no reason given"),
            })
        else:
            g = (curr_spend - prev_spend) / prev_spend * 100
            if growth_type == "MoM":
                formula = "(%s-%s)/%s*100 MoM" % (curr_spend, prev_spend, prev_spend)
            else:
                formula = "(%s-%s)/%s*100 YoY vs %s" % (
                    curr_spend, prev_spend, prev_spend, prev["period"])
            out.append({
                "period": r["period"], "ward": ward, "category": category,
                "actual_spend": str(curr_spend),
                "growth_pct": "%.1f%%" % g,
                "formula": formula,
                "status": "computed",
            })
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Analyzer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False, default=None)
    parser.add_argument("--category", required=False, default=None)
    parser.add_argument("--growth-type", required=False, default=None)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        rows = load_dataset(args.input)
        nulls = [r for r in rows if r["actual_spend"] is None]
        print("Null actual_spend rows: %d" % len(nulls))
        for n in nulls:
            print("  NULL %s | %s | %s | %s" % (
                n["period"], n["ward"], n["category"], n["notes"]))
        result = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "period", "ward", "category", "actual_spend",
            "growth_pct", "formula", "status"])
        w.writeheader()
        w.writerows(result)
    print("Done. Growth table written to %s" % args.output)


if __name__ == "__main__":
    main()
