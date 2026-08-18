"""
UC-0C Budget Growth Analyser
Built following the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Optional, Tuple


def load_dataset(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Skill: load_dataset
    Reads ward_budget.csv, validates columns, reports null count and details.
    Returns (data, null_report).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget dataset file not found: {file_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_report = []

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns in CSV: {missing}")

        for row_idx, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            budgeted = float(row["budgeted_amount"]) if row.get("budgeted_amount") else 0.0

            if raw_spend == "" or raw_spend.upper() == "NULL":
                actual_spend = None
                null_reason = row.get("notes", "").strip() or "Missing spend data"
                null_report.append({
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "null_reason": null_reason,
                    "line": row_idx,
                })
            else:
                try:
                    actual_spend = float(raw_spend)
                    null_reason = ""
                except ValueError:
                    actual_spend = None
                    null_reason = f"Unparseable value '{raw_spend}' in notes: {row.get('notes', '')}"
                    null_report.append({
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "null_reason": null_reason,
                        "line": row_idx,
                    })

            data.append({
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": budgeted,
                "actual_spend": actual_spend,
                "notes": row.get("notes", "").strip(),
                "null_reason": null_reason,
            })

    # Print null report to stdout before any computation
    print(f"=== NULL SPEND REPORT ({len(null_report)} null rows detected) ===")
    for item in null_report:
        print(f"  • Period: {item['period']} | Ward: {item['ward']} | Category: {item['category']} | Reason: {item['null_reason']}")
    print("=" * 60 + "\n")

    return data, null_report


def compute_growth(
    data: List[Dict], ward: str, category: str, growth_type: str
) -> List[Dict]:
    """
    Skill: compute_growth
    Filters dataset to specific ward and category, computes per-period growth rates with formulas.
    """
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("Growth type not specified. Please provide --growth-type MoM or --growth-type YoY.")

    # Filter rows by ward and category
    filtered = [
        row for row in data
        if row["ward"].lower() == ward.lower() and row["category"].lower() == category.lower()
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'. Check exact spelling."
        )

    # Sort by period chronologically
    filtered.sort(key=lambda x: x["period"])

    # Create period lookup map for YoY calculations
    period_map = {row["period"]: row for row in filtered}

    results = []

    for i, row in enumerate(filtered):
        curr_period = row["period"]
        curr_spend = row["actual_spend"]
        curr_null_reason = row["null_reason"]

        prev_spend = None
        prev_period = None

        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i - 1]
                prev_spend = prev_row["actual_spend"]
                prev_period = prev_row["period"]
        elif growth_type == "YoY":
            # Extract year and month, calculate previous year period
            parts = curr_period.split("-")
            if len(parts) == 2:
                year, month = int(parts[0]), parts[1]
                prev_yr_period = f"{year - 1:04d}-{month}"
                if prev_yr_period in period_map:
                    prev_row = period_map[prev_yr_period]
                    prev_spend = prev_row["actual_spend"]
                    prev_period = prev_yr_period

        growth_rate = None
        formula = ""
        null_reason_out = curr_null_reason

        if curr_spend is None:
            formula = "N/A — current period actual spend is NULL"
            growth_rate_str = "NULL"
        elif prev_period is None:
            formula = f"N/A — no prior {growth_type} period available"
            growth_rate_str = "N/A"
        elif prev_spend is None:
            formula = f"N/A — prior period ({prev_period}) actual spend is NULL"
            growth_rate_str = "NULL"
            null_reason_out = f"Prior period ({prev_period}) spend was NULL"
        else:
            diff = curr_spend - prev_spend
            rate = (diff / prev_spend) * 100.0
            growth_rate = round(rate, 2)
            growth_rate_str = f"{growth_rate:+.1f}%" if growth_rate != 0 else "0.0%"
            formula = f"({curr_spend} - {prev_spend}) / {prev_spend} * 100 = {growth_rate_str}"

        results.append({
            "period": curr_period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": curr_spend if curr_spend is not None else "NULL",
            "growth_type": growth_type,
            "growth_rate": growth_rate_str,
            "formula": formula,
            "null_reason": null_reason_out,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")

    args = parser.parse_args()

    # Enforcement Rule 1: Refuse aggregation across wards or categories
    if not args.ward or not args.category or args.ward.lower() == "all" or args.category.lower() == "all":
        print(
            "ERROR: Aggregation across wards/categories is not permitted. Please specify one ward and one category.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Enforcement Rule 4: Refuse if --growth-type is not specified or invalid
    if not args.growth_type or args.growth_type not in ["MoM", "YoY"]:
        print(
            "ERROR: Growth type not specified. Please provide --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 1: Load dataset & report nulls
    data, null_report = load_dataset(args.input)

    # Step 2: Compute growth for specified ward, category, and growth type
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Write results to output CSV
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "formula",
        "null_reason",
    ]

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth analysis completed. Results written to {args.output}")


if __name__ == "__main__":
    main()

