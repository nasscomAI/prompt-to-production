"""
UC-0C — Number That Looks Right
CRAFT-enforced: wrong aggregation level, silent null handling, formula assumption.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("Dataset is empty.")

    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    null_rows = []
    for row in rows:
        if row.get("actual_spend", "").strip() == "":
            null_rows.append(row)

    if null_rows:
        print(f"\n[NULL REPORT] {len(null_rows)} null actual_spend row(s) detected:", file=sys.stderr)
        for r in null_rows:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | notes: {r.get('notes','').strip()}", file=sys.stderr)
        print("", file=sys.stderr)

    return rows, null_rows


def compute_growth(rows: list, growth_type: str) -> list:
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be MoM or YoY.")

    sorted_rows = sorted(rows, key=lambda r: r["period"])
    results = []

    for i, row in enumerate(sorted_rows):
        period = row["period"]
        spend_raw = row.get("actual_spend", "").strip()

        if spend_raw == "":
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula": "N/A",
                "flag": "FLAGGED — null actual_spend",
            })
            continue

        current = float(spend_raw)

        if growth_type == "MoM":
            # Find previous month
            prev_row = None
            for j in range(i - 1, -1, -1):
                if sorted_rows[j].get("actual_spend", "").strip() != "":
                    prev_row = sorted_rows[j]
                    break

            if prev_row is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "growth_pct": "NULL",
                    "formula": "MoM: ((current - previous) / previous) * 100",
                    "flag": "NO_PRIOR_PERIOD",
                })
            else:
                previous = float(prev_row["actual_spend"])
                growth = ((current - previous) / previous) * 100
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "growth_pct": f"{growth:+.1f}%",
                    "formula": f"MoM: (({current:.1f} - {previous:.1f}) / {previous:.1f}) * 100",
                    "flag": "",
                })

        elif growth_type == "YoY":
            # Find same period prior year
            prior_period = f"{int(period[:4]) - 1}{period[4:]}"
            prior_row = next((r for r in sorted_rows if r["period"] == prior_period
                              and r.get("actual_spend", "").strip() != ""), None)

            if prior_row is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "growth_pct": "NULL",
                    "formula": "YoY: ((current - prior_year) / prior_year) * 100",
                    "flag": "NO_PRIOR_YEAR",
                })
            else:
                prior = float(prior_row["actual_spend"])
                growth = ((current - prior) / prior) * 100
                results.append({
                    "period": period,
                    "actual_spend": f"{current:.1f}",
                    "growth_pct": f"{growth:+.1f}%",
                    "formula": f"YoY: (({current:.1f} - {prior:.1f}) / {prior:.1f}) * 100",
                    "flag": "",
                })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name to analyse")
    parser.add_argument("--category",    required=True,  help="Exact category name to analyse")
    parser.add_argument("--growth-type", required=True,  choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-on-month) or YoY (year-on-year)")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    all_rows, _ = load_dataset(args.input)

    filtered = [r for r in all_rows if r["ward"] == args.ward and r["category"] == args.category]

    if not filtered:
        print(f"ERROR: No rows found for ward='{args.ward}' and category='{args.category}'.", file=sys.stderr)
        sys.exit(1)

    results = compute_growth(filtered, args.growth_type)

    out_fields = ["period", "actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()
