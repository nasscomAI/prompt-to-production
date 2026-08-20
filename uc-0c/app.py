"""
UC-0C — Number That Looks Right

Computes per-ward per-category month-over-month (MoM) growth from
ward_budget.csv and writes growth_output.csv.

Enforcement rules (from agents.md) implemented here:
  1. Never aggregate across wards or categories — refuse if asked.
  2. Flag every null actual_spend row BEFORE computing; report the null reason
     from the notes column; never compute a growth figure from a null.
  3. Show the formula used in every output row alongside the result.
  4. If --growth-type is not specified (or unsupported) — refuse, never guess.
"""
import argparse
import csv
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

AGGREGATE_WORDS = {"any", "all", "every", "total", "overall", "combined", "both", "across"}

GROWTH_TYPES = {"MoM", "YoY"}

OUTPUT_FIELDS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "previous_actual_spend",
    "growth_type",
    "growth_pct",
    "formula",
    "status",
]


def _is_aggregate(value: str) -> bool:
    return value.strip().lower() in AGGREGATE_WORDS


def _fmt(num) -> str:
    return "%.1f" % num


def load_dataset(input_path: str) -> list:
    """Read CSV, validate columns, and report null actual_spend rows."""
    if not os.path.isfile(input_path):
        print("Error: input file not found: %s" % input_path, file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("Error: input file contains no data rows.", file=sys.stderr)
        sys.exit(1)

    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        print("Error: missing required column(s): %s" % ", ".join(missing), file=sys.stderr)
        sys.exit(1)

    nulls = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    if nulls:
        print("WARNING: %d row(s) with null actual_spend (growth will NOT be computed for these):"
              % len(nulls))
        for r in nulls:
            note = (r.get("notes") or "").strip()
            print("  - %s | %s | %s | null reason: %s"
                  % (r["period"], r["ward"], r["category"], note or "(no reason given)"))

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Return a per-period growth table for one ward + one category.
    Each row: dict with OUTPUT_FIELDS keys. Nulls are flagged, never computed.
    """
    periods = {}
    for r in rows:
        if r["ward"].strip() == ward and r["category"].strip() == category:
            periods[r["period"].strip()] = r

    ordered = sorted(periods.items())  # sorted by period (YYYY-MM)

    results = []
    prev_actual = None
    prev_period = None
    for period, r in ordered:
        budgeted = (r.get("budgeted_amount") or "").strip()
        actual = (r.get("actual_spend") or "").strip()
        note = (r.get("notes") or "").strip()

        budgeted_f = float(budgeted) if budgeted else None
        actual_f = float(actual) if actual else None

        row = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": _fmt(budgeted_f) if budgeted_f is not None else "",
            "actual_spend": _fmt(actual_f) if actual_f is not None else "",
            "previous_actual_spend": _fmt(prev_actual) if prev_actual is not None else "",
            "growth_type": growth_type,
            "growth_pct": "",
            "formula": "n/a",
            "status": "",
        }

        if actual_f is None:
            row["status"] = "NULL actual_spend — not computed"
            if note:
                row["status"] += " | reason: %s" % note
        elif prev_actual is None:
            row["status"] = "No previous month data — not computed"
        elif prev_actual == 0:
            row["status"] = "Previous actual_spend is zero — division by zero, not computed"
        else:
            growth = (actual_f - prev_actual) / prev_actual * 100.0
            growth_r = round(growth, 1)
            if growth_r == -0.0:
                growth_r = 0.0
            row["growth_pct"] = _fmt(growth_r)
            row["formula"] = "%s = (%s - %s) / %s \u00d7 100" % (
                growth_type,
                _fmt(actual_f),
                _fmt(prev_actual),
                _fmt(prev_actual),
            )
            row["status"] = "computed"

        results.append(row)
        if actual_f is not None:
            prev_actual = actual_f
            prev_period = period

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget MoM Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward name (cross-ward aggregation is refused)")
    parser.add_argument("--category", required=True, help="Single category name (cross-category aggregation is refused)")
    parser.add_argument("--growth-type", required=True, choices=sorted(GROWTH_TYPES), help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if _is_aggregate(args.ward) or _is_aggregate(args.category):
        print("Error: cross-ward / cross-category aggregation is NOT permitted. "
              "Specify a single --ward and a single --category.", file=sys.stderr)
        sys.exit(1)

    if args.growth_type == "YoY":
        print("Error: YoY growth cannot be computed — the dataset covers a single year (2024) "
              "and has no prior-year values. Use --growth-type MoM.", file=sys.stderr)
        sys.exit(1)

    rows = load_dataset(args.input)

    wards = {r["ward"].strip().lower(): r["ward"].strip() for r in rows}
    categories = {r["category"].strip().lower(): r["category"].strip() for r in rows}

    ward_key = args.ward.strip().lower()
    category_key = args.category.strip().lower()
    if ward_key not in wards:
        print("Error: ward '%s' not found in dataset. Available wards: %s"
              % (args.ward, ", ".join(sorted(set(wards.values())))), file=sys.stderr)
        sys.exit(1)
    if category_key not in categories:
        print("Error: category '%s' not found in dataset. Available categories: %s"
              % (args.category, ", ".join(sorted(set(categories.values())))), file=sys.stderr)
        sys.exit(1)

    ward = wards[ward_key]
    category = categories[category_key]

    results = compute_growth(rows, ward, category, args.growth_type)

    if not results:
        print("Error: no data rows for ward '%s' / category '%s'." % (ward, category), file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print("Computed %s growth for ward '%s' / category '%s' -> %s"
          % (args.growth_type, ward, category, args.output))
    flagged = [r for r in results if r["status"] != "computed"]
    print("Rows flagged (not computed): %d" % len(flagged))


if __name__ == "__main__":
    main()