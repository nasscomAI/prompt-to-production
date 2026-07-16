"""
UC-0C app.py — Ward budget growth calculator.

Computes per-period growth of actual_spend for ONE ward + ONE category.
Enforcement (see agents.md):
  1. Refuses to aggregate across wards/categories — --ward and --category required.
  2. Flags every null actual_spend row (with its notes reason) before computing.
  3. Shows the substituted growth formula on every computed row.
  4. Refuses to run if --growth-type is not given — never assumes MoM or YoY.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ("MoM", "YoY")
OUTPUT_COLUMNS = ["period", "ward", "category", "actual_spend",
                  "growth_pct", "formula", "status", "null_reason"]


def refuse(message):
    print("REFUSED: " + message, file=sys.stderr)
    sys.exit(2)


def load_dataset(input_path):
    """Read the CSV, validate columns, and report every null actual_spend row."""
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                refuse("input file is missing required columns: " + ", ".join(missing))
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError("Input file not found: " + input_path)

    for row in rows:
        raw = (row.get("actual_spend") or "").strip()
        try:
            row["actual_spend"] = float(raw) if raw else None
        except ValueError:
            row["actual_spend"] = None

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print("NULL REPORT — {} row(s) with null actual_spend:".format(len(null_rows)))
    for r in null_rows:
        print("  {period} · {ward} · {category} — reason: {notes}".format(
            period=r["period"], ward=r["ward"], category=r["category"],
            notes=(r.get("notes") or "").strip() or "(no reason recorded)"))
    print()
    return rows


def compute_growth(rows, ward, category, growth_type):
    """Per-period growth for one ward + one category. Never aggregates."""
    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    if ward not in wards:
        refuse("ward '{}' not found. Available wards: {}".format(ward, "; ".join(wards)))
    if category not in categories:
        refuse("category '{}' not found. Available categories: {}".format(
            category, "; ".join(categories)))

    subset = sorted((r for r in rows if r["ward"] == ward and r["category"] == category),
                    key=lambda r: r["period"])

    if growth_type == "MoM":
        prior_of = {subset[i]["period"]: subset[i - 1] for i in range(1, len(subset))}
    else:  # YoY: prior period is the same month one year earlier
        by_period = {r["period"]: r for r in subset}
        prior_of = {}
        for r in subset:
            year, month = r["period"].split("-")
            prior_of[r["period"]] = by_period.get("{}-{}".format(int(year) - 1, month))

    results = []
    for r in subset:
        out = {"period": r["period"], "ward": ward, "category": category,
               "actual_spend": "" if r["actual_spend"] is None else r["actual_spend"],
               "growth_pct": "", "formula": "", "status": "", "null_reason": ""}
        prev = prior_of.get(r["period"])
        if r["actual_spend"] is None:
            out["status"] = "SKIPPED_NULL"
            out["null_reason"] = (r.get("notes") or "").strip() or "(no reason recorded)"
        elif prev is None:
            out["status"] = "NO_PRIOR_PERIOD"
            out["formula"] = "{} growth needs a prior period; none exists for {}".format(
                growth_type, r["period"])
        elif prev["actual_spend"] is None:
            out["status"] = "PREV_NULL"
            out["formula"] = "prior period {} actual_spend is null — cannot compute".format(
                prev["period"])
        else:
            curr, base = r["actual_spend"], prev["actual_spend"]
            pct = (curr - base) / base * 100
            out["growth_pct"] = round(pct, 1)
            out["formula"] = "{} = ({} - {}) / {} * 100 = {:+.1f}%".format(
                growth_type, curr, base, base, pct)
            out["status"] = "OK"
        results.append(out)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Per-ward, per-category budget growth calculator (UC-0C).")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward name (required — no aggregation)")
    parser.add_argument("--category", help="Exact category name (required — no aggregation)")
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY (required — never assumed)")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    if not args.growth_type:
        refuse("--growth-type not specified. Please choose MoM or YoY explicitly — "
               "the growth formula is never assumed.")
    if args.growth_type not in GROWTH_TYPES:
        refuse("unsupported --growth-type '{}'. Supported: {}".format(
            args.growth_type, ", ".join(GROWTH_TYPES)))

    rows = load_dataset(args.input)

    if not args.ward or not args.category:
        wards = sorted({r["ward"] for r in rows})
        categories = sorted({r["category"] for r in rows})
        refuse("aggregating across wards or categories is not allowed. "
               "Specify both --ward and --category.\n"
               "  Wards: {}\n  Categories: {}".format("; ".join(wards), "; ".join(categories)))

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    print("{} growth — {} · {}".format(args.growth_type, args.ward, args.category))
    for row in results:
        detail = row["formula"] if row["status"] != "SKIPPED_NULL" \
            else "null actual_spend — reason: " + row["null_reason"]
        print("  {} [{}] {}".format(row["period"], row["status"], detail))
    print("\nWrote {} row(s) to {}".format(len(results), args.output))


if __name__ == "__main__":
    main()
