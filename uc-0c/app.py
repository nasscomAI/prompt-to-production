"""
UC-0C app.py — Number That Looks Right
Built using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str):
    """
    Reads the ward budget CSV, validates columns, reports null rows.
    Returns (rows, null_report).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Budget file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        for col in REQUIRED_COLUMNS:
            if col not in headers:
                raise ValueError(f"Missing required column: {col}")

        rows = list(reader)

    null_rows = []
    for i, row in enumerate(rows):
        actual = row.get("actual_spend", "").strip()
        if actual == "":
            null_rows.append({
                "row_index": i + 2,
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "")
            })

    null_report = f"Found {len(null_rows)} rows with null actual_spend:\n"
    for nr in null_rows:
        null_report += f"  - {nr['period']}, {nr['ward']}, {nr['category']}: {nr['notes']}\n"

    return rows, null_report, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes growth for a specific ward and category.
    Returns list of output row dicts.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")

    filtered = [r for r in rows if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]

    if not filtered:
        available_wards = sorted(set(r["ward"] for r in rows))
        available_cats = sorted(set(r["category"] for r in rows))
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    filtered.sort(key=lambda r: r["period"])

    results = []
    prev_actual = None
    prev_period = None

    for row in filtered:
        actual_str = row.get("actual_spend", "").strip()
        budgeted = row["budgeted_amount"]
        period = row["period"]
        notes = row.get("notes", "").strip()

        if actual_str == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula": "N/A — actual_spend is null",
                "null_flag": "YES",
                "null_reason": notes
            })
            prev_actual = None
            prev_period = period
            continue

        actual = float(actual_str)

        if prev_actual is None:
            growth_pct = "N/A (first period)"
            formula = f"N/A — no previous period data for {growth_type}"
        else:
            if growth_type == "MoM":
                growth = ((actual - prev_actual) / prev_actual) * 100
                growth_pct = f"{growth:+.1f}%"
                formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100 = {growth:+.1f}%"
            else:
                growth = ((actual - prev_actual) / prev_actual) * 100
                growth_pct = f"{growth:+.1f}%"
                formula = f"(({actual} - {prev_actual}) / {prev_actual}) / {prev_actual}) * 100 = {growth:+.1f}%"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": str(actual),
            "growth_pct": growth_pct,
            "formula": formula,
            "null_flag": "NO",
            "null_reason": ""
        })

        prev_actual = actual
        prev_period = period

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C — Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 - Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_report, null_rows = load_dataset(args.input)
    print(null_report)

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "null_flag", "null_reason"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output written to {args.output}")
    print(f"Total rows: {len(results)}, Null rows flagged: {sum(1 for r in results if r['null_flag'] == 'YES')}")


if __name__ == "__main__":
    main()
