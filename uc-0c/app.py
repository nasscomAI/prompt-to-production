"""
UC-0C — Number That Looks Right
Guided by agents.md and skills.md RICE specification.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str) -> tuple:
    """
    Skill 1: load_dataset
    Reads CSV, validates required schema, detects all null rows, and returns dataset + null summary.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
    rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required columns. Must contain: {required_cols}")

        for idx, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.upper() == "NULL" or raw_spend is None:
                is_null = True
                spend_val = None
                null_rows.append({
                    "line": idx,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes", "")
                })
            else:
                is_null = False
                spend_val = float(raw_spend)

            budget_val = float(row.get("budgeted_amount", 0.0)) if row.get("budgeted_amount") else 0.0

            rows.append({
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": budget_val,
                "actual_spend": spend_val,
                "is_null": is_null,
                "notes": row.get("notes", "").strip()
            })

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill 2: compute_growth
    Calculates per-period growth for requested ward and category, returning formatted table with formulas and null flags.
    """
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type was not specified. System refuses to assume growth type without explicit instructions.")

    if growth_type.upper() != "MOM":
        raise ValueError(f"REFUSAL: Unsupported growth-type '{growth_type}'. Only 'MoM' growth computation is currently supported.")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    if not filtered:
        raise ValueError(f"No records found for Ward '{ward}' and Category '{category}'.")

    results = []
    prev_spend = None
    prev_is_null = True

    for item in filtered:
        period = item["period"]
        budget = item["budgeted_amount"]
        actual = item["actual_spend"]
        is_null = item["is_null"]
        notes = item["notes"]

        if is_null:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": f"{budget:.1f}",
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula_used": "N/A (Data missing)",
                "notes": f"NULL: {notes}" if notes else "NULL: Missing actual spend"
            })
            prev_spend = None
            prev_is_null = True
        else:
            actual_str = f"{actual:.1f}"
            if prev_is_null or prev_spend is None:
                growth_str = "N/A"
                formula_str = "N/A (Baseline period or previous spend null)"
            else:
                pct = ((actual - prev_spend) / prev_spend) * 100.0
                sign = "+" if pct > 0 else ""
                growth_str = f"{sign}{pct:.1f}%"
                formula_str = f"(({actual:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": f"{budget:.1f}",
                "actual_spend": actual_str,
                "growth_pct": growth_str,
                "formula_used": formula_str,
                "notes": notes
            })
            prev_spend = actual
            prev_is_null = False

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to input ward budget CSV")
    parser.add_argument("--ward", required=False, help="Specific ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Specific category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth calculation type (e.g. 'MoM')")
    parser.add_argument("--aggregate", action="store_true", help="Request all-ward aggregation")
    parser.add_argument("--output", default="growth_output.csv", help="Path to write output CSV file")
    args = parser.parse_args()

    # Rule 1: Refuse all-ward aggregation unless explicitly allowed
    if args.aggregate or (not args.ward and not args.category):
        print("REFUSAL ERROR: Aggregation across all wards or categories without explicit ward/category parameters is strictly forbidden by enforcement rules.")
        sys.exit(1)

    # Rule 4: Refuse if growth-type missing
    if not args.growth_type:
        print("REFUSAL ERROR: --growth-type parameter is missing. Please specify --growth-type MoM explicitly.")
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)
    print(f"Loaded {len(rows)} budget records. Detected {len(null_rows)} null actual_spend rows.")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula_used", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
