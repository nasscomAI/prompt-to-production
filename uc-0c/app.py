"""
UC-0C — Number That Looks Right
Computes month-over-month (MoM) growth for ward budget data.
Enforcement: per-ward per-category only, null flagging, formula shown, no silent aggregation.
"""
import argparse
import csv


def load_dataset(input_path: str) -> tuple:
    """
    Read budget CSV, validate columns, report nulls.
    Returns: (rows list, null_report list)
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Validate columns
        found_cols = set(reader.fieldnames) if reader.fieldnames else set()
        missing = required_cols - found_cols
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Found: {found_cols}")

        rows = list(reader)

    # Report nulls
    null_report = []
    for row in rows:
        actual = row.get("actual_spend", "").strip()
        if not actual:
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided").strip()
            })

    return rows, null_report


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM growth for a specific ward + category.
    Returns: list of result dicts with formula shown.
    """
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type: '{growth_type}'. Allowed: MoM")

    # Filter for this ward + category
    filtered = [
        row for row in data
        if row["ward"].strip() == ward and row["category"].strip() == category
    ]

    if not filtered:
        available_wards = sorted(set(r["ward"].strip() for r in data))
        available_cats = sorted(set(r["category"].strip() for r in data))
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row.get("notes", "").strip()

        # Check current null
        if not actual_str:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_spend": "",
                "formula": "N/A — actual_spend is NULL",
                "mom_growth_pct": "NULL",
                "flag": f"NULL: {notes if notes else 'No reason provided'}"
            })
            continue

        actual = float(actual_str)

        # First period — no previous
        if i == 0:
            results.append({
                "period": period,
                "actual_spend": str(actual),
                "previous_spend": "N/A",
                "formula": "N/A — first period, no previous month",
                "mom_growth_pct": "N/A",
                "flag": ""
            })
            continue

        # Check previous period null
        prev_actual_str = filtered[i - 1]["actual_spend"].strip()
        if not prev_actual_str:
            prev_notes = filtered[i - 1].get("notes", "").strip()
            results.append({
                "period": period,
                "actual_spend": str(actual),
                "previous_spend": "NULL",
                "formula": "N/A — previous period actual_spend is NULL",
                "mom_growth_pct": "NULL",
                "flag": f"NULL: previous period ({filtered[i-1]['period']}) has null actual_spend — {prev_notes if prev_notes else 'No reason'}"
            })
            continue

        prev_actual = float(prev_actual_str)
        if prev_actual == 0:
            results.append({
                "period": period,
                "actual_spend": str(actual),
                "previous_spend": str(prev_actual),
                "formula": "N/A — previous actual_spend is zero, division undefined",
                "mom_growth_pct": "N/A",
                "flag": "DIVISION_BY_ZERO"
            })
            continue

        # Compute MoM growth
        growth = ((actual - prev_actual) / prev_actual) * 100
        growth_rounded = round(growth, 1)
        sign = "+" if growth_rounded >= 0 else ""

        results.append({
            "period": period,
            "actual_spend": str(actual),
            "previous_spend": str(prev_actual),
            "formula": f"(({actual} - {prev_actual}) / {prev_actual}) × 100",
            "mom_growth_pct": f"{sign}{growth_rounded}%",
            "flag": ""
        })

    return results


def main(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    """Load data, report nulls, compute growth, write output."""
    if not growth_type:
        print("ERROR: --growth-type is required. Allowed values: MoM")
        print("Refusing to guess. Please specify --growth-type MoM")
        return

    print(f"Loading dataset from: {input_path}")
    data, null_report = load_dataset(input_path)
    print(f"Loaded {len(data)} rows.")

    # Report nulls upfront
    if null_report:
        print(f"\n⚠ WARNING: {len(null_report)} rows have NULL actual_spend:")
        for nr in null_report:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        print()

    # Compute growth
    print(f"Computing {growth_type} growth for: {ward} / {category}")
    results = compute_growth(data, ward, category, growth_type)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "previous_spend", "formula", "mom_growth_pct", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to: {output_path}")
    print(f"{len(results)} periods computed for {ward} / {category}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True, help="Ward name (exact match)")
    parser.add_argument("--category",    required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM")
    parser.add_argument("--output",      required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    main(args.input, args.ward, args.category, args.growth_type, args.output)
