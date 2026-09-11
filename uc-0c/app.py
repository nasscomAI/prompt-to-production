"""
UC-0C — Number That Looks Right
Computes month-over-month (or other, if extended) spend growth for a single,
explicitly specified ward and category from ward_budget.csv. Never
aggregates across wards/categories, never silently defaults growth-type,
always flags nulls with their reason, and always shows the formula used.
Implements the two skills defined in skills.md: load_dataset, compute_growth.
"""

import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

FORMULAS = {
    "MoM": "(current_period_spend - prior_period_spend) / prior_period_spend * 100",
}


def load_dataset(input_path, ward, category):
    try:
        with open(input_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                print(f"ERROR: input file is missing required column(s): {missing}", file=sys.stderr)
                sys.exit(1)
            all_rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for row in all_rows:
        if row.get("ward") == ward and row.get("category") == category:
            raw_spend = (row.get("actual_spend") or "").strip()
            actual_spend = None
            if raw_spend != "":
                try:
                    actual_spend = float(raw_spend)
                except ValueError:
                    actual_spend = None
            rows.append({
                "period": row.get("period"),
                "ward": row.get("ward"),
                "category": row.get("category"),
                "budgeted_amount": row.get("budgeted_amount"),
                "actual_spend": actual_spend,
                "notes": row.get("notes", ""),
            })

    if not rows:
        print(
            f"ERROR: no rows found for ward='{ward}' category='{category}'. "
            "Check the exact spelling (including en-dash in ward names) against the input file.",
            file=sys.stderr,
        )
        sys.exit(1)

    rows.sort(key=lambda r: r["period"])

    null_report = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"],
         "reason": r["notes"] or "null: no reason provided in notes column"}
        for r in rows if r["actual_spend"] is None
    ]

    if null_report:
        print(f"NOTE: {len(null_report)} null actual_spend row(s) found in this ward/category slice:")
        for n in null_report:
            print(f"  - {n['period']}: {n['reason']}")

    return rows, null_report


def compute_growth(rows, growth_type):
    if growth_type not in FORMULAS:
        print(
            f"ERROR: --growth-type '{growth_type}' is not supported. "
            f"Supported types: {list(FORMULAS.keys())}. This must be specified explicitly, never guessed.",
            file=sys.stderr,
        )
        sys.exit(1)

    formula_str = FORMULAS[growth_type]
    output_rows = []
    prior_spend = None
    prior_seen = False

    for row in rows:
        spend = row["actual_spend"]
        growth_pct = ""
        flag = ""

        if spend is None:
            flag = row["notes"] or "null: actual_spend missing"
        elif not prior_seen:
            flag = "no prior period to compare"
        elif prior_spend is None:
            flag = "prior period null — cannot compute growth"
        elif prior_spend == 0:
            flag = "prior period spend is zero — division undefined"
        else:
            growth_pct = round(((spend - prior_spend) / prior_spend) * 100, 2)

        output_rows.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": spend if spend is not None else "",
            "prior_period_spend": prior_spend if prior_spend is not None else "",
            "growth_pct": growth_pct,
            "formula_used": formula_str,
            "flag": flag,
        })

        prior_spend = spend
        prior_seen = True

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C ward/category budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name to filter on")
    parser.add_argument("--category", required=True, help="Exact category name to filter on")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type (e.g. MoM) — must be explicit, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input, args.ward, args.category)
    result = compute_growth(rows, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "prior_period_spend", "growth_pct", "formula_used", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"Computed {args.growth_type} growth for ward='{args.ward}', category='{args.category}'")
    print(f"Wrote {len(result)} row(s) to {args.output}")
    if null_report:
        print(f"{len(null_report)} row(s) flagged as null — see 'flag' column in output.")


if __name__ == "__main__":
    main()
