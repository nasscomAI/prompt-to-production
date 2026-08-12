"""
UC-0C app.py — NAIVE BASELINE (Control step).
Mirrors what "Calculate growth from the data." naively produces: silently
aggregates every ward and category into one citywide number per month,
silently skips (drops) rows with a null actual_spend instead of flagging
them, and picks a growth formula (MoM) without ever being asked. Kept here
temporarily to document the Control run; see git history.
"""
import argparse
import csv
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    # ward/category/growth-type accepted but silently ignored below --
    # naive behaviour always aggregates everything and always uses MoM.
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    args = parser.parse_args()

    totals = defaultdict(float)  # period -> summed actual_spend, nulls just skipped
    with open(args.input, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            spend = row.get("actual_spend", "").strip()
            if not spend:
                continue  # silently skip nulls -- no flag, no report
            totals[row["period"]] += float(spend)

    periods = sorted(totals)
    out_rows = []
    prev = None
    for p in periods:
        current = totals[p]
        growth = "" if prev is None else round((current - prev) / prev * 100, 1)
        out_rows.append({"period": p, "total_actual_spend": round(current, 1), "growth_pct": growth})
        prev = current

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["period", "total_actual_spend", "growth_pct"])
        w.writeheader()
        w.writerows(out_rows)
    print(f"Done. Growth written to {args.output}")


if __name__ == "__main__":
    main()
