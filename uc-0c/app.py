"""
UC-0C — Number That Looks Right (Ward Budget Analysis)
Built following RICE and CRAFT workflow to enforce granularity boundaries, explicit null auditing, and formula transparency.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str):
    """
    Loads dataset, checks columns, audits and reports null actual_spend rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset file not found: {input_path}")

    rows = []
    null_rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            actual = row.get("actual_spend", "").strip()
            if actual == "" or actual.lower() == "null":
                null_rows.append({
                    "line": idx,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes", "No reason provided")
                })
            rows.append(row)

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str):
    """
    Computes MoM or YoY growth for a single ward and category.
    Refuses all-ward aggregation and flags null records.
    """
    if not growth_type:
        print("ERROR [REFUSAL]: --growth-type must be explicitly specified (e.g. 'MoM' or 'YoY'). Formula assumption is prohibited.")
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"ERROR [REFUSAL]: Growth type '{growth_type}' not supported in single-year 2024 dataset. Please specify MoM.")
        sys.exit(1)

    if not ward or ward.lower() in ["all", "any", "total", "city"]:
        print("ERROR [REFUSAL]: All-ward aggregation is strictly prohibited. You must specify a single ward.")
        sys.exit(1)

    if not category or category.lower() in ["all", "any", "total"]:
        print("ERROR [REFUSAL]: Cross-category aggregation is strictly prohibited. You must specify a single category.")
        sys.exit(1)

    # Normalize ward and category matching
    filtered = [
        r for r in rows
        if r.get("ward", "").strip().lower() == ward.strip().lower()
        and r.get("category", "").strip().lower() == category.strip().lower()
    ]

    if not filtered:
        # Try relaxed matching for dashes
        clean_target_ward = ward.replace("–", "-").replace("—", "-").strip().lower()
        filtered = [
            r for r in rows
            if r.get("ward", "").replace("–", "-").replace("—", "-").strip().lower() == clean_target_ward
            and r.get("category", "").strip().lower() == category.strip().lower()
        ]

    if not filtered:
        print(f"ERROR: No records found matching ward '{ward}' and category '{category}'.")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda x: x.get("period", ""))

    output_rows = []
    prev_spend = None

    for r in filtered:
        period = r.get("period")
        budgeted = r.get("budgeted_amount")
        actual_str = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        if actual_str == "" or actual_str.lower() == "null":
            mom_growth_str = "NULL (Flagged)"
            formula_str = f"Missing spend: {notes}"
            prev_spend = None
        else:
            try:
                curr_spend = float(actual_str)
                if prev_spend is None:
                    mom_growth_str = "Base Period"
                    formula_str = "N/A (First period or preceding period null)"
                else:
                    growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
                    sign = "+" if growth_val > 0 else ""
                    mom_growth_str = f"{sign}{growth_val:.1f}%"
                    formula_str = f"(({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                prev_spend = curr_spend
            except ValueError:
                mom_growth_str = "ERROR"
                formula_str = "Invalid numeric format"
                prev_spend = None

        output_rows.append({
            "period": period,
            "ward": r.get("ward"),
            "category": r.get("category"),
            "budgeted_amount": budgeted,
            "actual_spend": actual_str if actual_str else "NULL",
            "mom_growth": mom_growth_str,
            "formula": formula_str,
            "notes": notes
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Name of single ward")
    parser.add_argument("--category", required=True, help="Name of single category")
    parser.add_argument("--growth-type", required=True, dest="growth_type", help="Growth metric: MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    print(f"Dataset loaded: {len(rows)} records. Found {len(null_rows)} deliberate null rows across dataset:")
    for nr in null_rows:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth", "formula", "notes"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nGrowth output successfully generated for '{args.ward}' - '{args.category}' ({args.growth_type}).")
    print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
