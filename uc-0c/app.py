"""
Application to analyze ward budget data and compute period-over-period growth metrics.
"""
# pylint: disable=line-too-long, too-many-locals, broad-exception-caught

import csv
import argparse
import sys
import os
from typing import Any, Dict, List, Optional


def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Reads the ward budget CSV file, validates required schema,
    and reports null values before returning structured data.
    """
    if not os.path.exists(file_path):
        print(f"Error: Input file missing or unreadable: {file_path}")
        sys.exit(1)

    required_columns: List[str] = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]
    data: List[Dict[str, Any]] = []
    null_rows: List[Dict[str, str]] = []

    try:
        with open(file_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            raw_fieldnames = reader.fieldnames
            if not raw_fieldnames:
                print("Error: CSV is empty or improperly formatted.")
                sys.exit(1)

            fieldnames: List[str] = list(raw_fieldnames)

            # Validate required schema
            missing_cols: List[str] = [
                c for c in required_columns if c not in fieldnames
            ]
            if missing_cols:
                print(f"Error: Missing required columns in input CSV: {missing_cols}")
                sys.exit(1)

            for row in reader:
                # Check if dataset appears pre-aggregated (e.g. ward or category is empty or 'Total')
                ward: str = str(row.get("ward", "")).strip()
                category: str = str(row.get("category", "")).strip()
                if not ward or ward.lower() == "all" or ward.lower() == "total":
                    print(
                        "Error: Dataset appears pre-aggregated or missing ward granularity. Refusing to proceed."
                    )
                    sys.exit(1)
                if (
                    not category
                    or category.lower() == "all"
                    or category.lower() == "total"
                ):
                    print(
                        "Error: Dataset appears pre-aggregated or missing category granularity. Refusing to proceed."
                    )
                    sys.exit(1)

                # Check for null actual_spend
                actual_spend_raw: str = str(row.get("actual_spend", "")).strip()
                actual_spend: Optional[float] = None

                if not actual_spend_raw or actual_spend_raw.upper() == "NULL":
                    null_rows.append(
                        {
                            "period": str(row.get("period", "")),
                            "ward": ward,
                            "category": category,
                            "notes": str(row.get("notes", "")),
                        }
                    )
                else:
                    try:
                        actual_spend = float(actual_spend_raw)
                    except ValueError:
                        print(f"Error: Invalid actual_spend value '{actual_spend_raw}'")
                        sys.exit(1)

                record: Dict[str, Any] = {
                    "period": str(row.get("period", "")).strip(),
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": str(row.get("budgeted_amount", "")).strip(),
                    "actual_spend": actual_spend,
                    "notes": str(row.get("notes", "")),
                }
                data.append(record)

    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

    return {"data": data, "null_summary": {"count": len(null_rows), "rows": null_rows}}


def compute_growth(
    dataset: Dict[str, Any], target_ward: str, target_category: str, growth_type: str
) -> List[Dict[str, str]]:
    """
    Computes per-period growth for a specified ward and category
    using a defined growth type and returns results with formulas.
    """
    if not growth_type:
        print(
            "Error: --growth-type is not specified. Refusing to guess. Please provide a growth type (e.g., MoM)."
        )
        sys.exit(1)

    if growth_type.lower() not in ["mom"]:
        print(
            f"Error: Unsupported growth type '{growth_type}'. Currently only 'MoM' is explicitly supported."
        )
        # We could support YoY etc, but we don't guess.
        sys.exit(1)

    if not target_ward or target_ward.lower() in ["any", "all", "total"]:
        print(
            f"Error: Cross-ward aggregation requested ({target_ward}). System must REFUSE per enforcement rules."
        )
        sys.exit(1)

    if not target_category or target_category.lower() in ["any", "all", "total"]:
        print(
            f"Error: Cross-category aggregation requested ({target_category}). System must REFUSE per enforcement rules."
        )
        sys.exit(1)

    # Filter data to the strict per-ward and per-category granularity
    filtered_data: List[Dict[str, Any]] = [
        row
        for row in dataset["data"]
        if row["ward"] == target_ward and row["category"] == target_category
    ]

    if not filtered_data:
        print(
            f"Error: No data found for Ward: '{target_ward}' and Category: '{target_category}'. Validation error."
        )
        sys.exit(1)

    # Sort sequentially by period (e.g. "2024-01", "2024-02")
    filtered_data.sort(key=lambda x: str(x["period"]))

    output_rows: List[Dict[str, str]] = []

    for i, current_row in enumerate(filtered_data):
        period: str = str(current_row["period"])
        spend: Optional[float] = current_row["actual_spend"]
        notes: str = str(current_row["notes"])

        row_output: Dict[str, str] = {
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": "" if spend is None else f"{spend:.2f}",
            "growth_value": "n/a",
            "formula_used": "n/a",
            "null_flag": "",
            "null_reason": "",
        }

        # Null handling
        if spend is None:
            row_output["null_flag"] = "NULL_VALUES_FLAGGED"
            row_output["null_reason"] = notes
            row_output["formula_used"] = "Skipped computation due to null actual_spend"
            output_rows.append(row_output)
            continue

        # Compute growth
        if growth_type.lower() == "mom":
            if i == 0:
                row_output["formula_used"] = "Insufficient prior data (first period)"
                output_rows.append(row_output)
                continue

            prev_row: Dict[str, Any] = filtered_data[i - 1]
            prev_spend: Optional[float] = prev_row["actual_spend"]

            if prev_spend is None:
                row_output["formula_used"] = (
                    "Insufficient prior data (previous period was null)"
                )
                output_rows.append(row_output)
                continue

            if prev_spend == 0.0:
                row_output["formula_used"] = (
                    "Cannot divide by zero (previous spend is 0)"
                )
                output_rows.append(row_output)
                continue

            growth: float = ((spend - prev_spend) / prev_spend) * 100

            sign: str = "+" if growth > 0 else ""
            row_output["growth_value"] = f"{sign}{growth:.1f}%"
            # Explicit formula as enforced by rules
            row_output["formula_used"] = (
                f"(({spend:.2f} - {prev_spend:.2f}) / {prev_spend:.2f}) * 100"
            )
            output_rows.append(row_output)

    return output_rows


def main() -> None:
    """
    Main execution entry point: parses arguments, loads dataset,
    computes growth metrics, and outputs to CSV.
    """
    parser = argparse.ArgumentParser(
        description="Deterministic per-ward per-category Growth Analyzer"
    )
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument(
        "--ward", required=False, help="Explicit target ward"
    )  # Optional so we can catch missing and refuse
    parser.add_argument("--category", required=False, help="Explicit target category")
    parser.add_argument(
        "--growth-type", required=False, help="Growth calculation type (e.g. MoM)"
    )
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    # Load dataset
    print(f"Loading dataset from: {args.input}")
    dataset_result: Dict[str, Any] = load_dataset(args.input)

    null_summary: Dict[str, Any] = dataset_result["null_summary"]
    if null_summary["count"] > 0:
        print(
            f"Validation Note: Found {null_summary['count']} deliberate null rows before computing."
        )
        for nr in null_summary["rows"]:
            print(
                f"  - {nr['period']} | {nr['ward']} | {nr['category']} -> Reason: {nr['notes']}"
            )

    # Enforce ward and category presence
    target_ward: str = getattr(args, "ward", "") or ""
    target_category: str = getattr(args, "category", "") or ""
    growth_type: str = getattr(args, "growth_type", "") or ""

    if not target_ward or not target_category:
        print(
            "Error: Aggregation across wards or categories without explicit instructions is forbidden. You must provide strict --ward and --category."
        )
        sys.exit(1)

    # Compute Growth
    results: List[Dict[str, str]] = compute_growth(
        dataset=dataset_result,
        target_ward=target_ward,
        target_category=target_category,
        growth_type=growth_type,
    )

    # Save to output
    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, mode="w", newline="", encoding="utf-8") as outfile:
            fieldnames: List[str] = [
                "period",
                "ward",
                "category",
                "actual_spend",
                "growth_value",
                "formula_used",
                "null_flag",
                "null_reason",
            ]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Successfully wrote {len(results)} rows to {args.output}")
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
