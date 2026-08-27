"""
UC-0C app.py — Budget Growth Calculator
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""

import argparse
import csv
import sys

VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(file_path: str):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if not r.get("actual_spend", "").strip()]
    if null_rows:
        print(f"NOTICE: {len(null_rows)} rows have null actual_spend and will be flagged, not computed:")
        for r in null_rows:
            reason = r.get("notes", "").strip() or "no reason given in notes column"
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {reason}")

    return rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    if not ward or ward.strip().upper() == "ALL":
        raise ValueError(
            "REFUSED: --ward must specify a single ward. Aggregating across all "
            "wards is not permitted by this tool's enforcement rules."
        )
    if not category or category.strip().upper() == "ALL":
        raise ValueError(
            "REFUSED: --category must specify a single category. Aggregating "
            "across all categories is not permitted by this tool's enforcement rules."
        )
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"REFUSED: --growth-type must be one of {sorted(VALID_GROWTH_TYPES)}. "
            "This tool never guesses a growth type."
        )

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No rows found for ward='{ward}' category='{category}'. Check exact spelling.")

    filtered.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in filtered}

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        budgeted = row["budgeted_amount"]
        actual_raw = row.get("actual_spend", "").strip()

        if not actual_raw:
            reason = row.get("notes", "").strip() or "no reason given in notes column"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "",
                "growth_type": growth_type,
                "growth_pct": "",
                "formula": "N/A - actual_spend is null",
                "flag": f"NOT_COMPUTED - {reason}",
            })
            continue

        actual = float(actual_raw)

        prev_row = None
        if growth_type == "MoM" and i > 0:
            prev_row = filtered[i - 1]
        elif growth_type == "YoY":
            year, month = period.split("-")
            prev_period = f"{int(year) - 1}-{month}"
            prev_row = by_period.get(prev_period)

        if prev_row is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "growth_type": growth_type,
                "growth_pct": "",
                "formula": "N/A - no prior period available for comparison",
                "flag": "NOT_COMPUTED - insufficient history",
            })
            continue

        prev_actual_raw = prev_row.get("actual_spend", "").strip()
        if not prev_actual_raw:
            prev_reason = prev_row.get("notes", "").strip() or "no reason given in notes column"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "growth_type": growth_type,
                "growth_pct": "",
                "formula": f"N/A - prior period {prev_row['period']} actual_spend is null",
                "flag": f"NOT_COMPUTED - prior period null ({prev_reason})",
            })
            continue

        prev_actual = float(prev_actual_raw)
        growth_pct = ((actual - prev_actual) / prev_actual) * 100 if prev_actual != 0 else None

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "growth_type": growth_type,
            "growth_pct": round(growth_pct, 1) if growth_pct is not None else "",
            "formula": f"(({actual} - {prev_actual}) / {prev_actual}) * 100 [vs {prev_row['period']}]"
                       if growth_pct is not None else "N/A - previous value is zero",
            "flag": "" if growth_pct is not None else "NOT_COMPUTED - division by zero",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, choices=sorted(VALID_GROWTH_TYPES),
                         help="MoM or YoY — must be specified explicitly, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, getattr(args, "growth_type"))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "growth_type", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Wrote {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()
