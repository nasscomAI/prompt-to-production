"""
UC-0C — Number That Looks Right
RICE-compliant municipal budget growth analyzer guided by agents.md and skills.md.
"""
import argparse
import csv
import sys
import os


def load_dataset(input_path: str):
    """
    Reads budget CSV file, validates schema, and reports null actual_spend rows.
    Returns list of row dicts and list of null reports.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    rows = []
    null_reports = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            rows.append(row)
            actual = (row.get("actual_spend") or "").strip()
            if not actual:
                null_reports.append({
                    "row_index": idx,
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": "category",
                    "notes": row.get("notes", "No reason provided")
                })

    return rows, null_reports


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes period-over-period growth for a specific ward and category.
    Strictly refuses all-ward or all-category aggregations.
    """
    # 1. Enforcement Check: Refuse All-Ward or All-Category Aggregations
    if not ward or ward.lower() in ["all", "any", "all-ward", "all wards"]:
        raise ValueError("REFUSAL: Aggregating growth across all wards is strictly forbidden by RICE enforcement rules.")

    if not category or category.lower() in ["all", "any", "all-category", "all categories"]:
        raise ValueError("REFUSAL: Aggregating growth across all categories is strictly forbidden by RICE enforcement rules.")

    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError("REFUSAL: --growth-type must be explicitly specified ('MoM' or 'YoY'). Guessing formulas is strictly forbidden.")

    # 2. Filter dataset for specific ward & category
    filtered = [
        r for r in rows
        if r.get("ward", "").strip() == ward.strip() and r.get("category", "").strip() == category.strip()
    ]

    filtered.sort(key=lambda x: x.get("period", ""))

    output_rows = []
    prev_spend = None

    for r in filtered:
        period = r.get("period", "")
        budgeted = r.get("budgeted_amount", "")
        actual_raw = (r.get("actual_spend") or "").strip()
        notes = r.get("notes", "").strip()

        if not actual_raw:
            actual_str = "NULL"
            growth_pct = "NULL - NOT COMPUTED"
            formula = f"NULL ({notes})" if notes else "NULL - Missing spend"
            prev_spend = None
        else:
            try:
                curr_spend = float(actual_raw)
                actual_str = f"{curr_spend:.1f}"

                if prev_spend is None:
                    growth_pct = "N/A (First Period)" if prev_spend is None else "N/A (Previous Period Null)"
                    formula = "N/A"
                else:
                    growth_val = ((curr_spend - prev_spend) / prev_spend) * 100
                    growth_pct = f"{growth_val:+.1f}%"
                    formula = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"

                prev_spend = curr_spend
            except ValueError:
                actual_str = "INVALID"
                growth_pct = "ERROR"
                formula = "Invalid numeric data"
                prev_spend = None

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_str,
            "growth_pct": growth_pct,
            "formula": formula,
            "notes": notes
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", help="Growth type ('MoM' or 'YoY')")
    parser.add_argument("--output", required=True, help="Path to save growth_output.csv")
    args = parser.parse_args()

    # Enforcement: Check missing required arguments before processing
    if not args.growth_type:
        print("ERROR: --growth-type was not specified. RICE enforcement forbids guessing formula types.", file=sys.stderr)
        sys.exit(1)

    if not args.ward or not args.category:
        print("ERROR: --ward and --category must both be specified. All-ward/all-category aggregation is strictly refused.", file=sys.stderr)
        sys.exit(1)

    try:
        rows, null_reports = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "notes"]

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth analysis written to {args.output}")


if __name__ == "__main__":
    main()
