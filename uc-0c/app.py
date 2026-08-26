#!/usr/bin/env python3
"""
UC-0C — Number That Looks Right
Civic Tech Edition · Vibe Coding Workshop

Computes month-on-month (MoM) or year-on-year (YoY) growth of actual_spend for a
SPECIFIC ward + category. The naive prompt "calculate growth from the data"
returns one blended number across all wards, silently ignores the 5 null rows,
and picks a formula without being asked. This app refuses to do any of that.

Enforcement:
  1. Never aggregate across wards or categories. An all-ward request is REFUSED.
  2. Every null actual_spend row is flagged (with the reason from `notes`) and
     never silently treated as zero or skipped without notice.
  3. The exact formula is shown alongside every computed row.
  4. If --growth-type is missing, the program refuses and asks (never guesses).

Run:
    python app.py --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
        --growth-type MoM --output growth_output.csv
"""

import argparse
import csv
import sys

ALL_TOKENS = {"all", "*", "all wards", "all categories", "total", "everything"}


def load_dataset(path):
    """
    skill: load_dataset
    Reads the CSV, validates columns, and reports null actual_spend rows BEFORE
    returning. Returns (rows, null_rows).
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if (r.get("actual_spend") or "").strip() == ""]
    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(null_rows)}")
    for r in null_rows:
        print(f"  NULL  {r['period']} · {r['ward']} · {r['category']}  "
              f"-> reason: {r.get('notes','').strip() or '(no reason given)'}")
    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """
    skill: compute_growth
    Returns a per-period table for ONE ward + category, with the formula shown.
    Refuses all-ward / all-category requests. Flags null rows instead of computing.
    """
    if ward.strip().lower() in ALL_TOKENS or category.strip().lower() in ALL_TOKENS:
        raise PermissionError(
            "REFUSED: cross-ward / cross-category aggregation is not permitted. "
            "Specify exactly one ward and one category."
        )

    growth_type = growth_type.upper()
    if growth_type not in {"MOM", "YOY"}:
        raise ValueError(f"Unknown growth-type '{growth_type}'. Use MoM or YoY.")

    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not subset:
        raise ValueError(f"No rows for ward='{ward}', category='{category}'. "
                         "Check exact spelling (en-dash – in ward names).")
    subset.sort(key=lambda r: r["period"])

    # index by period for lag lookup
    by_period = {r["period"]: r for r in subset}
    lag = 1 if growth_type == "MOM" else 12

    results = []
    periods = [r["period"] for r in subset]
    for i, r in enumerate(subset):
        period = r["period"]
        cur_raw = (r.get("actual_spend") or "").strip()

        # current value null -> flag, do not compute
        if cur_raw == "":
            results.append({
                "ward": ward, "category": category, "period": period,
                "actual_spend": "NULL", "growth_type": growth_type,
                "growth_pct": "FLAGGED — not computed",
                "formula": "n/a (current value is null)",
                "note": r.get("notes", "").strip(),
            })
            continue

        cur = float(cur_raw)

        # find the comparison period `lag` positions earlier in the sorted list
        prev_idx = i - lag
        if prev_idx < 0:
            results.append({
                "ward": ward, "category": category, "period": period,
                "actual_spend": cur, "growth_type": growth_type,
                "growth_pct": "n/a (no prior period)",
                "formula": "n/a (first period in range)",
                "note": "",
            })
            continue

        prev_row = subset[prev_idx]
        prev_raw = (prev_row.get("actual_spend") or "").strip()
        if prev_raw == "":
            results.append({
                "ward": ward, "category": category, "period": period,
                "actual_spend": cur, "growth_type": growth_type,
                "growth_pct": "FLAGGED — prior period is null",
                "formula": f"n/a (comparison period {prev_row['period']} is null)",
                "note": prev_row.get("notes", "").strip(),
            })
            continue

        prev = float(prev_raw)
        growth = (cur - prev) / prev * 100.0
        results.append({
            "ward": ward, "category": category, "period": period,
            "actual_spend": cur, "growth_type": growth_type,
            "growth_pct": f"{growth:+.1f}%",
            "formula": f"({cur} - {prev}) / {prev} * 100  [vs {prev_row['period']}]",
            "note": "",
        })

    return results


def write_output(results, path):
    cols = ["ward", "category", "period", "actual_spend", "growth_type",
            "growth_pct", "formula", "note"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(results)
    print(f"\nWrote {len(results)} rows -> {path}")
    for r in results:
        print(f"  {r['period']}  {str(r['actual_spend']):>6}  {r['growth_pct']:<24} {r['formula']}")


def main():
    p = argparse.ArgumentParser(description="UC-0C Budget Growth")
    p.add_argument("--input", required=True)
    p.add_argument("--ward", required=True)
    p.add_argument("--category", required=True)
    # NOTE: growth-type intentionally NOT given a default — missing => refuse.
    p.add_argument("--growth-type", dest="growth_type", default=None,
                   help="MoM or YoY. Required — the program refuses to guess.")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    if not args.growth_type:
        print("REFUSED: --growth-type was not specified. "
              "I will not guess between MoM and YoY. "
              "Re-run with --growth-type MoM  or  --growth-type YoY.",
              file=sys.stderr)
        sys.exit(2)

    try:
        rows, _ = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(results, args.output)
    except FileNotFoundError:
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
