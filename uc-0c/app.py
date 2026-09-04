"""
UC-0C — Number That Looks Right
App implementation using RICE framework, agents.md, and skills.md.
Performs deterministic, per-ward per-category growth calculations
with explicit formulas, strict refusal of cross-ward aggregation,
and transparent null handling.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Any, Set


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "growth_type",
    "comparison_period",
    "comparison_actual_spend",
    "formula",
    "growth_percent",
    "status",
    "notes",
]

FORBIDDEN_WILDCARDS = {"all", "any", "*", "all wards", "all categories", "total", "combined", "n/a"}


def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Ingests and validates ward_budget.csv.
    Reports dataset stats and logs every null actual_spend row.
    Skill: load_dataset
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input budget file not found: {file_path}")

    rows = []
    null_rows = []
    wards: Set[str] = set()
    categories: Set[str] = set()

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        
        # Validate column headers
        if not reader.fieldnames:
            raise ValueError(f"Empty CSV file: {file_path}")
        
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {missing_cols}")

        for line_no, row in enumerate(reader, start=2):
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            budgeted = row.get("budgeted_amount", "").strip()
            actual = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()

            if ward:
                wards.add(ward)
            if category:
                categories.add(category)

            cleaned_row = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": notes,
            }
            rows.append(cleaned_row)

            if not actual:
                null_rows.append({
                    "line_number": line_no,
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budgeted,
                    "notes": notes,
                })

    print(f"Loaded {len(rows)} rows from {file_path}.")
    print(f"Discovered {len(wards)} wards and {len(categories)} categories.")
    print(f"Identified {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: '{nr['notes']}'")

    return {
        "file_path": file_path,
        "rows": rows,
        "wards": sorted(list(wards)),
        "categories": sorted(list(categories)),
        "null_rows": null_rows,
    }


def compute_growth(dataset: Dict[str, Any], ward: str, category: str, growth_type: str) -> List[Dict[str, Any]]:
    """
    Computes period-over-period growth for exactly one ward and category.
    Never aggregates across wards or categories.
    Skill: compute_growth
    """
    if not ward or ward.strip().lower() in FORBIDDEN_WILDCARDS:
        raise ValueError(
            f"Cross-ward or ambiguous aggregation is prohibited. Requested ward: '{ward}'. "
            f"You must specify exactly one valid ward from: {dataset['wards']}"
        )

    if not category or category.strip().lower() in FORBIDDEN_WILDCARDS:
        raise ValueError(
            f"Cross-category or ambiguous aggregation is prohibited. Requested category: '{category}'. "
            f"You must specify exactly one valid category from: {dataset['categories']}"
        )

    if ward not in dataset["wards"]:
        raise ValueError(f"Unknown ward: '{ward}'. Available wards: {dataset['wards']}")

    if category not in dataset["categories"]:
        raise ValueError(f"Unknown category: '{category}'. Available categories: {dataset['categories']}")

    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Unsupported growth-type: '{growth_type}'. Must be 'MoM' or 'YoY'.")

    # Filter strictly to the requested ward and category time series
    series = [
        r for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]

    # Sort chronologically by period
    series.sort(key=lambda r: r["period"])

    period_lookup = {r["period"]: r for r in series}
    results = []

    for i, row in enumerate(series):
        period = row["period"]
        budgeted = row["budgeted_amount"]
        actual_raw = row["actual_spend"]
        notes = row["notes"]

        current_val = float(actual_raw) if actual_raw else None

        if growth_type == "MoM":
            if i == 0:
                # First period has no prior month
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budgeted,
                    "actual_spend": actual_raw,
                    "growth_type": growth_type,
                    "comparison_period": "",
                    "comparison_actual_spend": "",
                    "formula": "N/A - first period in series",
                    "growth_percent": "",
                    "status": "FIRST_PERIOD",
                    "notes": notes,
                })
            else:
                prev_row = series[i - 1]
                comp_period = prev_row["period"]
                prev_actual_raw = prev_row["actual_spend"]
                prev_val = float(prev_actual_raw) if prev_actual_raw else None

                if current_val is None:
                    # Current row is null
                    formula_msg = f"N/A - actual_spend is null ({notes})" if notes else "N/A - actual_spend is null"
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": "",
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": prev_actual_raw,
                        "formula": formula_msg,
                        "growth_percent": "",
                        "status": "MISSING_CURRENT",
                        "notes": notes,
                    })
                elif prev_val is None:
                    # Comparison row is null
                    prev_notes = prev_row.get("notes", "")
                    formula_msg = (
                        f"N/A - comparison period {comp_period} actual_spend is null ({prev_notes})"
                        if prev_notes else f"N/A - comparison period {comp_period} actual_spend is null"
                    )
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual_raw,
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": "",
                        "formula": formula_msg,
                        "growth_percent": "",
                        "status": "MISSING_COMPARISON",
                        "notes": notes,
                    })
                elif prev_val == 0:
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual_raw,
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": prev_actual_raw,
                        "formula": f"(({current_val} - {prev_val}) / {prev_val}) * 100 [Division by zero]",
                        "growth_percent": "",
                        "status": "ZERO_DENOMINATOR",
                        "notes": notes,
                    })
                else:
                    growth = ((current_val - prev_val) / prev_val) * 100.0
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual_raw,
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": prev_actual_raw,
                        "formula": f"(({current_val} - {prev_val}) / {prev_val}) * 100",
                        "growth_percent": f"{growth:.1f}",
                        "status": "COMPUTED",
                        "notes": notes,
                    })

        elif growth_type == "YoY":
            # Determine 12-month prior period (e.g. 2024-05 -> 2023-05)
            try:
                year_str, month_str = period.split("-")
                prior_year = int(year_str) - 1
                comp_period = f"{prior_year:04d}-{month_str}"
            except Exception:
                comp_period = "UNKNOWN_PRIOR_PERIOD"

            if comp_period not in period_lookup:
                # Prior year period not in 2024 dataset
                results.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budgeted,
                    "actual_spend": actual_raw,
                    "growth_type": growth_type,
                    "comparison_period": comp_period,
                    "comparison_actual_spend": "",
                    "formula": f"N/A - prior year period {comp_period} not available in dataset",
                    "growth_percent": "",
                    "status": "NO_PRIOR_YEAR_DATA",
                    "notes": notes,
                })
            else:
                prior_row = period_lookup[comp_period]
                prior_actual_raw = prior_row["actual_spend"]
                prior_val = float(prior_actual_raw) if prior_actual_raw else None

                if current_val is None:
                    formula_msg = f"N/A - actual_spend is null ({notes})" if notes else "N/A - actual_spend is null"
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": "",
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": prior_actual_raw,
                        "formula": formula_msg,
                        "growth_percent": "",
                        "status": "MISSING_CURRENT",
                        "notes": notes,
                    })
                elif prior_val is None:
                    prior_notes = prior_row.get("notes", "")
                    formula_msg = (
                        f"N/A - prior year period {comp_period} actual_spend is null ({prior_notes})"
                        if prior_notes else f"N/A - prior year period {comp_period} actual_spend is null"
                    )
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual_raw,
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": "",
                        "formula": formula_msg,
                        "growth_percent": "",
                        "status": "MISSING_COMPARISON",
                        "notes": notes,
                    })
                elif prior_val == 0:
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual_raw,
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": prior_actual_raw,
                        "formula": f"(({current_val} - {prior_val}) / {prior_val}) * 100 [Division by zero]",
                        "growth_percent": "",
                        "status": "ZERO_DENOMINATOR",
                        "notes": notes,
                    })
                else:
                    growth = ((current_val - prior_val) / prior_val) * 100.0
                    results.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "budgeted_amount": budgeted,
                        "actual_spend": actual_raw,
                        "growth_type": growth_type,
                        "comparison_period": comp_period,
                        "comparison_actual_spend": prior_actual_raw,
                        "formula": f"(({current_val} - {prior_val}) / {prior_val}) * 100",
                        "growth_percent": f"{growth:.1f}",
                        "status": "COMPUTED",
                        "notes": notes,
                    })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Expenditure Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific budget category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
        help="Growth calculation type (MoM or YoY). Mandatory."
    )
    parser.add_argument("--output", required=True, help="Path to write output growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for res in results:
            writer.writerow(res)

    print(f"\nSuccessfully wrote {len(results)} growth records to {args.output}")


if __name__ == "__main__":
    main()
