"""
UC-0C — Municipal Budget Growth Analysis Agent
Conforms strictly to agents.md, skills.md, and README.md.

Skills defined:
  - load_dataset: Reads CSV, validates required columns, and flags null actual_spend rows with notes.
  - compute_growth: Computes period-over-period spend growth for a specific ward and category,
                    outputting a per-period table with explicit formula documentation and refusal guards.
"""

import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


FORBIDDEN_AGGREGATION_TERMS = {
    "all",
    "total",
    "overall",
    "aggregate",
    "all wards",
    "all categories",
    "combined",
}


def load_dataset(file_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Skill: load_dataset
    Reads the municipal budget CSV, validates required columns, and identifies/reports
    null actual spend rows with their notes before returning data.

    Args:
        file_path: Path to input CSV file.

    Returns:
        Tuple of (all_records, null_records).

    Raises:
        FileNotFoundError: If the input CSV file does not exist.
        ValueError: If file is empty or missing required schema columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    ]

    records: List[Dict[str, str]] = []
    null_records: List[Dict[str, str]] = []

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Input file is empty or missing header: {file_path}")

        fieldnames = [c.strip() for c in reader.fieldnames]
        missing = [col for col in required_columns if col not in fieldnames]
        if missing:
            raise ValueError(
                f"Missing required columns in dataset: {missing}. Found: {fieldnames}"
            )

        for row_idx, row in enumerate(reader, start=1):
            clean_row = {k.strip(): (v.strip() if v is not None else "") for k, v in row.items()}
            records.append(clean_row)

            # Check for null actual_spend
            actual_spend_val = clean_row.get("actual_spend", "")
            if not actual_spend_val or actual_spend_val.upper() in ["NULL", "NONE", "NA", "N/A"]:
                null_records.append(
                    {
                        "row": str(row_idx),
                        "period": clean_row.get("period", ""),
                        "ward": clean_row.get("ward", ""),
                        "category": clean_row.get("category", ""),
                        "notes": clean_row.get("notes", "No reason provided in notes"),
                    }
                )

    return records, null_records


def print_null_report(null_records: List[Dict[str, str]]) -> None:
    """Prints a structured report of detected null rows and reasons."""
    print("=" * 80)
    print(f"DATASET VALIDATION: Found {len(null_records)} row(s) with null actual_spend:")
    print("=" * 80)
    for item in null_records:
        print(
            f" - Period: {item['period']:<7} | Ward: {item['ward']:<24} "
            f"| Category: {item['category']:<26} | Note: {item['notes']}"
        )
    print("=" * 80)


def validate_input_request(
    records: List[Dict[str, str]],
    ward: Optional[str],
    category: Optional[str],
    growth_type: Optional[str],
) -> None:
    """
    Validates user request against enforcement rules:
      1. Never aggregate across wards or categories.
      2. Refuse if --growth-type is missing.
      3. Refuse if ward or category is missing or invalid.
    """
    # 1. Check growth_type
    if not growth_type or not growth_type.strip():
        print(
            "\n[REFUSAL - MISSING GROWTH TYPE]\n"
            "Error: --growth-type is not specified.\n"
            "Enforcement Rule: Growth type must be explicitly specified (e.g. --growth-type MoM).\n"
            "The system refuses to silently guess or assume a default formula. Please provide --growth-type MoM or YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    normalized_growth = growth_type.strip().upper()
    if normalized_growth not in ["MOM", "YOY"]:
        print(
            f"\n[REFUSAL - UNSUPPORTED GROWTH TYPE]\n"
            f"Error: Unsupported growth type '{growth_type}'.\n"
            f"Supported growth types: MoM (Month-over-Month), YoY (Year-over-Year).",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Check ward
    if not ward or not ward.strip():
        print(
            "\n[REFUSAL - MISSING WARD]\n"
            "Error: --ward is required.\n"
            "Enforcement Rule: Output must be a per-ward, per-category table. Refusing to calculate without an explicit ward.",
            file=sys.stderr,
        )
        sys.exit(1)

    if ward.strip().lower() in FORBIDDEN_AGGREGATION_TERMS:
        print(
            "\n[REFUSAL - CROSS-WARD AGGREGATION FORBIDDEN]\n"
            f"Error: Requested ward '{ward}' requests an aggregated summary.\n"
            "Enforcement Rule: Never aggregate across wards unless explicitly instructed — refusing cross-ward aggregation.\n"
            "Please specify a single, specific municipal ward.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 3. Check category
    if not category or not category.strip():
        print(
            "\n[REFUSAL - MISSING CATEGORY]\n"
            "Error: --category is required.\n"
            "Enforcement Rule: Output must be a per-ward, per-category table. Refusing to calculate without an explicit category.",
            file=sys.stderr,
        )
        sys.exit(1)

    if category.strip().lower() in FORBIDDEN_AGGREGATION_TERMS:
        print(
            "\n[REFUSAL - CROSS-CATEGORY AGGREGATION FORBIDDEN]\n"
            f"Error: Requested category '{category}' requests an aggregated summary.\n"
            "Enforcement Rule: Never aggregate across categories unless explicitly instructed — refusing cross-category aggregation.\n"
            "Please specify a single, specific budget category.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 4. Verify presence in dataset
    available_wards = sorted(list({r["ward"] for r in records if r["ward"]}))
    available_categories = sorted(list({r["category"] for r in records if r["category"]}))

    if ward.strip() not in available_wards:
        print(
            f"\n[ERROR - UNKNOWN WARD]\n"
            f"Ward '{ward}' not found in dataset.\n"
            f"Available wards:\n" + "\n".join(f"  - {w}" for w in available_wards),
            file=sys.stderr,
        )
        sys.exit(1)

    if category.strip() not in available_categories:
        print(
            f"\n[ERROR - UNKNOWN CATEGORY]\n"
            f"Category '{category}' not found in dataset.\n"
            f"Available categories:\n" + "\n".join(f"  - {c}" for c in available_categories),
            file=sys.stderr,
        )
        sys.exit(1)


def compute_growth(
    records: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
    output_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth
    Computes period-over-period spend growth for a specific ward and category,
    returning a per-period table with explicit formula documentation.

    Args:
        records: List of budget record dictionaries.
        ward: Target ward name.
        category: Target category name.
        growth_type: Growth metric type (e.g. "MoM").
        output_path: Optional destination path for CSV output.

    Returns:
        List of structured result row dictionaries.
    """
    # Filter dataset for requested ward and category
    filtered = [
        r for r in records if r.get("ward") == ward and r.get("category") == category
    ]

    # Sort chronologically by period
    filtered.sort(key=lambda x: x.get("period", ""))

    results: List[Dict[str, Any]] = []

    for i, row in enumerate(filtered):
        period = row.get("period", "")
        budgeted_raw = row.get("budgeted_amount", "")
        actual_raw = row.get("actual_spend", "")
        note = row.get("notes", "")

        budgeted_val = float(budgeted_raw) if budgeted_raw else 0.0

        # Check if actual spend is null
        is_current_null = not actual_raw or actual_raw.upper() in ["NULL", "NONE", "NA", "N/A"]

        if is_current_null:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": f"{budgeted_val:.1f}",
                    "actual_spend": "NULL",
                    "growth_rate": "NULL (Flagged)",
                    "formula": "N/A (actual_spend is NULL)",
                    "notes": note if note else "Null actual spend flagged",
                }
            )
            continue

        current_actual = float(actual_raw)

        # Handle MoM growth
        if growth_type.upper() == "MOM":
            if i == 0:
                # First period - Baseline
                results.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": f"{budgeted_val:.1f}",
                        "actual_spend": f"{current_actual:.1f}",
                        "growth_rate": "N/A (Baseline)",
                        "formula": "N/A (First period — baseline)",
                        "notes": note,
                    }
                )
            else:
                prev_row = filtered[i - 1]
                prev_actual_raw = prev_row.get("actual_spend", "")
                is_prev_null = (
                    not prev_actual_raw
                    or prev_actual_raw.upper() in ["NULL", "NONE", "NA", "N/A"]
                )

                if is_prev_null:
                    prev_period = prev_row.get("period", "")
                    results.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "budgeted_amount": f"{budgeted_val:.1f}",
                            "actual_spend": f"{current_actual:.1f}",
                            "growth_rate": "N/A (Prior period NULL)",
                            "formula": f"N/A (Prior period {prev_period} spend is NULL)",
                            "notes": f"Cannot compute MoM: prior period ({prev_period}) spend was NULL",
                        }
                    )
                else:
                    prev_actual = float(prev_actual_raw)
                    diff = current_actual - prev_actual
                    if prev_actual != 0:
                        growth_pct = (diff / prev_actual) * 100
                        sign = "+" if growth_pct > 0 else ""
                        growth_str = f"{sign}{growth_pct:.1f}%"
                        formula_str = (
                            f"({current_actual:.1f} - {prev_actual:.1f}) / "
                            f"{prev_actual:.1f} * 100 = {growth_str}"
                        )
                    else:
                        growth_str = "N/A (Div by 0)"
                        formula_str = f"({current_actual:.1f} - 0.0) / 0.0 * 100"

                    results.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "budgeted_amount": f"{budgeted_val:.1f}",
                            "actual_spend": f"{current_actual:.1f}",
                            "growth_rate": growth_str,
                            "formula": formula_str,
                            "notes": note,
                        }
                    )
        elif growth_type.upper() == "YOY":
            # YoY comparison (same month previous year)
            curr_year, curr_month = period.split("-")
            prev_year = str(int(curr_year) - 1)
            prev_period = f"{prev_year}-{curr_month}"

            prev_row_match = next((r for r in filtered if r.get("period") == prev_period), None)
            if not prev_row_match:
                results.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": f"{budgeted_val:.1f}",
                        "actual_spend": f"{current_actual:.1f}",
                        "growth_rate": "N/A (Baseline)",
                        "formula": f"N/A (Prior year period {prev_period} not in dataset)",
                        "notes": note,
                    }
                )
            else:
                prev_actual_raw = prev_row_match.get("actual_spend", "")
                is_prev_null = (
                    not prev_actual_raw
                    or prev_actual_raw.upper() in ["NULL", "NONE", "NA", "N/A"]
                )
                if is_prev_null:
                    results.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "budgeted_amount": f"{budgeted_val:.1f}",
                            "actual_spend": f"{current_actual:.1f}",
                            "growth_rate": "N/A (Prior year NULL)",
                            "formula": f"N/A (Prior year period {prev_period} spend is NULL)",
                            "notes": f"Cannot compute YoY: prior year ({prev_period}) spend was NULL",
                        }
                    )
                else:
                    prev_actual = float(prev_actual_raw)
                    diff = current_actual - prev_actual
                    if prev_actual != 0:
                        growth_pct = (diff / prev_actual) * 100
                        sign = "+" if growth_pct > 0 else ""
                        growth_str = f"{sign}{growth_pct:.1f}%"
                        formula_str = (
                            f"({current_actual:.1f} - {prev_actual:.1f}) / "
                            f"{prev_actual:.1f} * 100 = {growth_str}"
                        )
                    else:
                        growth_str = "N/A (Div by 0)"
                        formula_str = f"({current_actual:.1f} - 0.0) / 0.0 * 100"

                    results.append(
                        {
                            "period": period,
                            "ward": ward,
                            "category": category,
                            "budgeted_amount": f"{budgeted_val:.1f}",
                            "actual_spend": f"{current_actual:.1f}",
                            "growth_rate": growth_str,
                            "formula": formula_str,
                            "notes": note,
                        }
                    )

    # Save to CSV if output path provided
    if output_path:
        fieldnames = [
            "period",
            "ward",
            "category",
            "budgeted_amount",
            "actual_spend",
            "growth_rate",
            "formula",
            "notes",
        ]
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    return results


def print_results_table(
    results: List[Dict[str, Any]], ward: str, category: str, growth_type: str
) -> None:
    """Displays output in a clean, verifiable terminal table."""
    print(f"\nGrowth Analysis Table ({growth_type})")
    print(f"Ward:     {ward}")
    print(f"Category: {category}")
    print("-" * 125)
    header = (
        f"{'Period':<9} | {'Budgeted':<9} | {'Actual':<8} | {'Growth Rate':<22} | "
        f"{'Formula Used':<40} | {'Notes'}"
    )
    print(header)
    print("-" * 125)
    for r in results:
        period = r["period"]
        budgeted = r["budgeted_amount"]
        actual = r["actual_spend"]
        growth = r["growth_rate"]
        formula = r["formula"]
        notes = r["notes"]
        print(
            f"{period:<9} | {budgeted:<9} | {actual:<8} | {growth:<22} | "
            f"{formula:<40} | {notes}"
        )
    print("-" * 125)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0C: Municipal Ward Budget Growth Analysis Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file (e.g. ../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--ward",
        required=False,
        help="Target municipal ward name (e.g. 'Ward 1 – Kasba')",
    )
    parser.add_argument(
        "--category",
        required=False,
        help="Target budget category (e.g. 'Roads & Pothole Repair')",
    )
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        help="Growth calculation formula type: MoM or YoY",
    )
    parser.add_argument(
        "--output",
        required=False,
        default="growth_output.csv",
        help="Destination path for output CSV table (default: growth_output.csv)",
    )

    args = parser.parse_args()

    # Step 1: Load dataset and validate columns and null rows (Skill: load_dataset)
    try:
        records, null_records = load_dataset(args.input)
    except Exception as e:
        print(f"\n[ERROR - DATASET LOAD FAILED]\n{e}", file=sys.stderr)
        sys.exit(1)

    print_null_report(null_records)

    # Step 2: Validate input arguments and enforcement conditions
    validate_input_request(records, args.ward, args.category, args.growth_type)

    # Step 3: Compute period growth (Skill: compute_growth)
    results = compute_growth(
        records=records,
        ward=args.ward.strip(),
        category=args.category.strip(),
        growth_type=args.growth_type.strip(),
        output_path=args.output,
    )

    # Step 4: Display results table
    print_results_table(
        results=results,
        ward=args.ward.strip(),
        category=args.category.strip(),
        growth_type=args.growth_type.strip(),
    )
    print(f"\nOutput successfully written to: {args.output}\n")


if __name__ == "__main__":
    main()
