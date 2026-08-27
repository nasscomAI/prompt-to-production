"""
UC-0C — Number That Looks Right
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str):
    """
    Reads the CSV, validates columns, reports null count and which rows,
    BEFORE any computation happens.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Input file is missing required columns: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if r["actual_spend"] in ("", None)]
    print(f"[load_dataset] Loaded {len(rows)} rows.")
    print(f"[load_dataset] Found {len(null_rows)} row(s) with null actual_spend:")
    for r in null_rows:
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes'] or '(no reason given)'}")

    return rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Computes per-period growth for ONE ward + ONE category only.
    Refuses (raises) if ward/category are missing or growth_type is invalid.
    Never aggregates across wards or categories.
    Every output row shows the formula used.
    """
    if not ward or not category:
        raise SystemExit(
            "REFUSED: ward and category must both be specified explicitly. "
            "This system never aggregates across wards or categories. "
            "Re-run with --ward \"<ward name>\" --category \"<category name>\"."
        )
    if growth_type not in ("MoM", "YoY"):
        raise SystemExit(
            "REFUSED: --growth-type must be exactly 'MoM' or 'YoY'. "
            "The system will not guess which formula to apply."
        )

    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not subset:
        raise SystemExit(
            f"REFUSED: no rows found for ward='{ward}' category='{category}'. "
            "Check the exact spelling (including the en-dash in ward names)."
        )
    subset.sort(key=lambda r: r["period"])

    def spend(r):
        return None if r["actual_spend"] in ("", None) else float(r["actual_spend"])

    by_period = {r["period"]: r for r in subset}
    results = []

    for r in subset:
        period = r["period"]
        curr = spend(r)

        if growth_type == "MoM":
            y, m = period.split("-")
            y, m = int(y), int(m)
            prev_y, prev_m = (y, m - 1) if m > 1 else (y - 1, 12)
            prev_period = f"{prev_y:04d}-{prev_m:02d}"
        else:  # YoY
            y, m = period.split("-")
            prev_period = f"{int(y) - 1:04d}-{m}"

        prev_row = by_period.get(prev_period)
        prev = spend(prev_row) if prev_row else None

        if curr is None:
            growth_pct, flag = None, "NULL_CURRENT"
            note = r["notes"] or "actual_spend is null for this period; not computed."
        elif prev_row is None:
            growth_pct, flag = None, "NO_PRIOR_PERIOD"
            note = f"No data for prior period {prev_period}; growth not computed."
        elif prev is None:
            growth_pct, flag = None, "NULL_PRIOR"
            note = f"Prior period {prev_period} has null actual_spend; growth not computed."
        elif prev == 0:
            growth_pct, flag = None, "DIV_BY_ZERO"
            note = f"Prior period {prev_period} actual_spend is 0; growth undefined."
        else:
            growth_pct = round((curr - prev) / prev * 100, 1)
            flag = ""
            note = f"formula: ({curr} - {prev}) / {prev} * 100"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": r["actual_spend"] or "NULL",
            "growth_type": growth_type,
            "growth_pct": growth_pct if growth_pct is not None else "",
            "flag": flag,
            "note": note,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False, default=None)
    parser.add_argument("--category", required=False, default=None)
    parser.add_argument("--growth-type", required=False, default=None, choices=[None, "MoM", "YoY"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "growth_type", "growth_pct", "flag", "note"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output} "
          f"(scope: ward='{args.ward}', category='{args.category}', type={args.growth_type})")


if __name__ == "__main__":
    main()