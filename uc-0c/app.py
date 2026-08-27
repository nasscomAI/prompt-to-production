"""
UC-0C — Number That Looks Right
Ward Budget Metrics Analyst built according to RICE -> agents.md -> skills.md workflow.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str):
    """
    Skill: load_dataset
    Reads CSV, validates columns, and reports all null actual_spend rows prior to computation.
    Returns: tuple (records, null_reports)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    records = []
    null_reports = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for idx, row in enumerate(reader, start=2):
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            notes = row.get("notes", "").strip()

            try:
                budgeted_amount = float(row.get("budgeted_amount", 0.0))
            except (ValueError, TypeError):
                budgeted_amount = 0.0

            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.upper() == "NULL":
                actual_spend = None
                null_reports.append({
                    "line": idx,
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "notes": notes or "No reason provided in dataset."
                })
            else:
                try:
                    actual_spend = float(raw_spend)
                except ValueError:
                    actual_spend = None
                    null_reports.append({
                        "line": idx,
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "notes": f"Invalid numerical spend value: '{raw_spend}'"
                    })

            records.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": notes
            })

    return records, null_reports


def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: compute_growth
    Computes period-over-period growth for a specific ward and category.
    Enforces strict scoping: refuses all-ward or all-category aggregation requests.
    """
    if not ward or not ward.strip():
        raise ValueError("Refusal Enforcement: --ward must be explicitly specified. Aggregation across all wards is strictly refused.")
    if not category or not category.strip():
        raise ValueError("Refusal Enforcement: --category must be explicitly specified. Aggregation across all categories is strictly refused.")
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError("Refusal Enforcement: --growth-type must be specified as 'MoM' or 'YoY'. System will not guess formula.")

    growth_type = growth_type.upper()

    # Filter for target ward and category
    filtered = [r for r in records if r["ward"].lower() == ward.lower() and r["category"].lower() == category.lower()]
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    period_offset = 1 if growth_type == "MOM" else 12

    for i, curr in enumerate(filtered):
        curr_period = curr["period"]
        curr_ward = curr["ward"]
        curr_cat = curr["category"]
        budgeted = curr["budgeted_amount"]
        curr_spend = curr["actual_spend"]
        curr_notes = curr["notes"]

        if curr_spend is None:
            output_rows.append({
                "period": curr_period,
                "ward": curr_ward,
                "category": curr_cat,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": "NULL",
                "growth_pct": "N/A",
                "formula": "N/A (Current actual_spend is NULL)",
                "notes": f"FLAGGED NULL: {curr_notes}" if curr_notes else "FLAGGED NULL"
            })
            continue

        if i < period_offset:
            output_rows.append({
                "period": curr_period,
                "ward": curr_ward,
                "category": curr_cat,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": f"{curr_spend:.1f}",
                "growth_pct": "N/A",
                "formula": f"N/A (First {growth_type} period in dataset)",
                "notes": curr_notes
            })
            continue

        prev = filtered[i - period_offset]
        prev_spend = prev["actual_spend"]

        if prev_spend is None or prev_spend == 0:
            output_rows.append({
                "period": curr_period,
                "ward": curr_ward,
                "category": curr_cat,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": f"{curr_spend:.1f}",
                "growth_pct": "N/A",
                "formula": f"N/A (Previous period {prev['period']} actual_spend was NULL or zero)",
                "notes": curr_notes
            })
            continue

        growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
        sign = "+" if growth_val > 0 else ""
        growth_str = f"{sign}{growth_val:.1f}%"
        formula_str = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"

        output_rows.append({
            "period": curr_period,
            "ward": curr_ward,
            "category": curr_cat,
            "budgeted_amount": f"{budgeted:.1f}",
            "actual_spend": f"{curr_spend:.1f}",
            "growth_pct": growth_str,
            "formula": formula_str,
            "notes": curr_notes
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Metrics Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth calculation type ('MoM' or 'YoY')")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Load dataset and report nulls pre-computation
    records, null_reports = load_dataset(args.input)

    print("=" * 70)
    print("PRE-COMPUTATION NULL DATASET REPORT:")
    print(f"Total null actual_spend rows detected: {len(null_reports)}")
    for null_item in null_reports:
        print(f"  • Period: {null_item['period']} | Ward: {null_item['ward']} | Category: {null_item['category']} -> Reason: {null_item['notes']}")
    print("=" * 70)

    try:
        results = compute_growth(records, args.ward, args.category, args.growth_type)
    except ValueError as err:
        print(f"\n[ENFORCEMENT REFUSAL]: {err}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Growth metrics output written to {args.output}")


if __name__ == "__main__":
    main()
