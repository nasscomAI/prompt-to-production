"""
UC-0C app.py — Budget Growth Computation & Variance Analysis.

Operational Boundaries & Enforcement:
1. Granular Non-Aggregation: Refuses cross-ward or cross-category combined aggregations.
2. Explicit Null Handling: Pre-flags null actual_spend rows and annotates with notes reasons. Never treats nulls as zero.
3. Transparent Formula Citation: Outputs explicit mathematical formulas for all computed periods.
4. Parameter Verification: Validates required arguments (--input, --ward, --category, --growth-type, --output) and refuses execution if ambiguous.
"""

import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


def load_dataset(file_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Skill: load_dataset
    Reads the municipal budget CSV file, validates required schema headers,
    identifies and reports null actual_spend counts and their corresponding rows/reasons.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at path: {file_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    records: List[Dict[str, str]] = []
    null_records: List[Dict[str, str]] = []

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Input file {file_path} is empty or has no header row.")

        fieldnames_set = set(reader.fieldnames)
        missing_columns = required_columns - fieldnames_set
        if missing_columns:
            raise ValueError(
                f"Schema validation failed. Missing required columns: {', '.join(sorted(missing_columns))}"
            )

        for line_num, row in enumerate(reader, start=2):
            records.append(row)
            actual_val = row.get("actual_spend", "").strip()
            if actual_val == "" or actual_val.lower() in ("null", "none", "nan"):
                null_records.append(
                    {
                        "row_num": str(line_num),
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "notes": row.get("notes", "No reason specified"),
                    }
                )

    print("=" * 70)
    print(f"DATASET LOADED: {file_path}")
    print(f"Total Rows: {len(records)}")
    print(f"Null 'actual_spend' Rows Detected: {len(null_records)}")
    print("=" * 70)

    if null_records:
        print("Flagged Null Rows (Prior to computation):")
        for nr in null_records:
            print(
                f"  • Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: {nr['notes']}"
            )
        print("=" * 70)

    return records, null_records


def compute_growth(
    records: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
    output_path: str,
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth
    Filters budget data for a specific ward and category, calculates period-over-period
    growth (MoM) with explicit formula citations, flags null rows, and outputs a CSV.
    """
    # 1. Enforcement: Refuse cross-ward or cross-category combined aggregation
    aggregation_keywords = {"all", "total", "all wards", "all categories", "combined", "aggregate"}
    if ward.strip().lower() in aggregation_keywords:
        raise ValueError(
            f"Refusal: Cross-ward aggregation ('{ward}') is strictly prohibited. "
            "Granular per-ward breakdown is required by agents.md enforcement rules."
        )
    if category.strip().lower() in aggregation_keywords:
        raise ValueError(
            f"Refusal: Cross-category aggregation ('{category}') is strictly prohibited. "
            "Granular per-category breakdown is required by agents.md enforcement rules."
        )

    # 2. Parameter Verification: Validate growth-type
    normalized_growth_type = growth_type.strip().upper()
    if normalized_growth_type != "MOM":
        raise ValueError(
            f"Unsupported or ambiguous growth-type: '{growth_type}'. "
            "Currently only 'MoM' (Month-over-Month) is supported. Never assume YoY or default formulas."
        )

    # 3. Filter for target ward and category
    filtered_records = [
        r for r in records
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered_records:
        available_wards = sorted(list(set(r["ward"] for r in records)))
        available_categories = sorted(list(set(r["category"] for r in records)))
        raise ValueError(
            f"No matching records found for Ward: '{ward}' and Category: '{category}'.\n"
            f"Available Wards: {available_wards}\n"
            f"Available Categories: {available_categories}"
        )

    # Sort chronologically by period
    filtered_records.sort(key=lambda x: x["period"])

    results: List[Dict[str, Any]] = []

    for t, current_row in enumerate(filtered_records):
        period = current_row["period"]
        budgeted = float(current_row["budgeted_amount"]) if current_row["budgeted_amount"].strip() else 0.0
        raw_actual = current_row["actual_spend"].strip()
        notes = current_row.get("notes", "").strip()

        # Check if current actual_spend is null
        is_current_null = (raw_actual == "" or raw_actual.lower() in ("null", "none", "nan"))

        if is_current_null:
            actual_display = "NULL"
            growth_rate = "NULL"
            status = f"FLAGGED: {notes if notes else 'Null value'}"
            formula = f"Cannot compute: actual_spend[{period}] is NULL ({notes})"
        elif t == 0:
            # Baseline period (first month)
            actual_val = float(raw_actual)
            actual_display = f"{actual_val:.1f}"
            growth_rate = "N/A (Baseline)"
            status = "BASELINE"
            formula = "Baseline period (t=0) — no prior period"
        else:
            actual_val = float(raw_actual)
            actual_display = f"{actual_val:.1f}"
            prev_row = filtered_records[t - 1]
            prev_raw_actual = prev_row["actual_spend"].strip()
            is_prev_null = (prev_raw_actual == "" or prev_raw_actual.lower() in ("null", "none", "nan"))

            if is_prev_null:
                # Prior period was null, cannot compute period-over-period growth
                growth_rate = "NULL (Prior period null)"
                status = f"FLAGGED: Prior period {prev_row['period']} was NULL"
                formula = f"Cannot compute: prior period ({prev_row['period']}) actual_spend was NULL"
            else:
                prev_val = float(prev_raw_actual)
                if prev_val == 0.0:
                    growth_rate = "N/A (Div by zero)"
                    status = "DIVISION_BY_ZERO"
                    formula = f"(actual_spend[{period}] - actual_spend[{prev_row['period']}]) / actual_spend[{prev_row['period']}] * 100 = ({actual_val} - 0) / 0"
                else:
                    growth_pct = ((actual_val - prev_val) / prev_val) * 100.0
                    sign = "+" if growth_pct > 0 else ""
                    growth_rate = f"{sign}{growth_pct:.1f}%"
                    status = "COMPUTED"
                    formula = (
                        f"(actual_spend[{period}] - actual_spend[{prev_row['period']}]) / "
                        f"actual_spend[{prev_row['period']}] * 100 = "
                        f"({actual_val:.1f} - {prev_val:.1f}) / {prev_val:.1f} * 100"
                    )

        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": f"{budgeted:.1f}",
            "actual_spend": actual_display,
            "growth_type": normalized_growth_type,
            "growth_rate": growth_rate,
            "status": status,
            "notes": notes,
            "formula": formula,
        }
        results.append(result_row)

    # Write output to CSV
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "status",
        "notes",
        "formula",
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary table to console
    print(f"\nGROWTH OUTPUT GENERATED: {output_path}")
    print("-" * 110)
    print(f"{'Period':<8} | {'Ward':<22} | {'Category':<24} | {'Actual':<8} | {'Growth':<15} | {'Formula / Reason'}")
    print("-" * 110)
    for r in results:
        print(
            f"{r['period']:<8} | {r['ward']:<22} | {r['category']:<24} | {r['actual_spend']:<8} | {r['growth_rate']:<15} | {r['formula']}"
        )
    print("-" * 110)

    return results


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute granular per-ward and per-category budget growth without unauthorized aggregation or silent null handling."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input budget CSV file (e.g. ../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Target ward name (e.g. 'Ward 1 – Kasba')",
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Target category name (e.g. 'Roads & Pothole Repair')",
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type (e.g. 'MoM'). Must be specified explicitly.",
    )
    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Path to output CSV file (default: growth_output.csv)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    try:
        records, _ = load_dataset(args.input)
        compute_growth(
            records=records,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
            output_path=args.output,
        )
    except Exception as e:
        print(f"\n[ERROR / REFUSAL]: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
