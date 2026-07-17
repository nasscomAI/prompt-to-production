"""
UC-0C - Number That Looks Right

Computes month-over-month (MoM) or year-over-year (YoY) growth rates
for ward-level municipal budget data. Strictly per-ward per-category,
flags null rows, shows formula. Operates per agents.md / skills.md.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> list:
    """Read ward budget CSV, validate columns, report nulls, return data."""
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
                missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
                print(f"Error: Missing required columns: {missing}", file=sys.stderr)
                sys.exit(1)
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Report null actual_spend rows
    null_rows = [r for r in data if r["actual_spend"].strip() == ""]
    if null_rows:
        print(f"Data quality report: {len(null_rows)} null actual_spend rows found:")
        for r in null_rows:
            reason = r.get("notes", "").strip() or "No reason provided"
            print(f"  {r['period']} | {r['ward']} | {r['category']} | Reason: {reason}")
    else:
        print("Data quality report: No null actual_spend rows found.")

    return data


def compute_growth(data: list, ward: str, category: str, growth_type: str, output_path: str):
    """Compute growth for a specific ward + category + growth_type, write to CSV."""
    # Validate growth_type
    if growth_type not in ("MoM", "YoY"):
        print(f"Error: --growth-type must be 'MoM' or 'YoY', got '{growth_type}'", file=sys.stderr)
        print("Please specify --growth-type MoM or --growth-type YoY", file=sys.stderr)
        sys.exit(1)

    # Filter data for this ward + category
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in data))
        available_cats = sorted(set(r["category"] for r in data))
        print(f"Error: No data found for ward='{ward}', category='{category}'", file=sys.stderr)
        print(f"Available wards: {available_wards}", file=sys.stderr)
        print(f"Available categories: {available_cats}", file=sys.stderr)
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    formula_str = "MoM = (current - previous) / previous * 100" if growth_type == "MoM" else "YoY = (current - same_month_prior_year) / same_month_prior_year * 100"

    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row.get("notes", "").strip()

        # Current period null check
        if actual_str == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "previous_spend": "",
                "growth_rate": f"N/A — null data ({notes or 'no reason'})",
                "formula": formula_str,
                "notes_flag": notes,
            })
            continue

        actual = float(actual_str)

        # Find previous period
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual}",
                    "previous_spend": "",
                    "growth_rate": "N/A — no previous period",
                    "formula": formula_str,
                    "notes_flag": "",
                })
                continue
            prev_row = filtered[i - 1]
        else:
            # YoY: same month, previous year
            year, month = period.split("-")
            prev_period = f"{int(year) - 1}-{month}"
            prev_candidates = [r for r in filtered if r["period"] == prev_period]
            if not prev_candidates:
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual}",
                    "previous_spend": "",
                    "growth_rate": "N/A — no prior year data",
                    "formula": formula_str,
                    "notes_flag": "",
                })
                continue
            prev_row = prev_candidates[0]

        prev_actual_str = prev_row["actual_spend"].strip()
        prev_notes = prev_row.get("notes", "").strip()

        # Previous period null check
        if prev_actual_str == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual}",
                "previous_spend": "",
                "growth_rate": f"N/A — previous period null ({prev_notes or 'no reason'})",
                "formula": formula_str,
                "notes_flag": f"Previous period ({prev_row['period']}) is null",
            })
            continue

        prev_actual = float(prev_actual_str)

        if prev_actual == 0:
            growth_rate = "N/A — division by zero (previous spend is 0)"
        else:
            growth = ((actual - prev_actual) / prev_actual) * 100
            growth_rate = f"{growth:+.2f}%"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual}",
            "previous_spend": f"{prev_actual}",
            "growth_rate": growth_rate,
            "formula": formula_str,
            "notes_flag": "",
        })

    # Write output
    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend",
                  "growth_rate", "formula", "notes_flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Computed {growth_type} growth for {ward} / {category}: {len(results)} periods.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    data = load_dataset(args.input)
    compute_growth(data, args.ward, args.category, args.growth_type, args.output)
    print(f"Done. Results written to {args.output}")
