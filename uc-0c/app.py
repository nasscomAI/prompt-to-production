"""
UC-0C — Number That Looks Right
Granular municipal budget growth analytics adhering to RICE enforcement rules:
- Prohibits cross-ward and cross-category aggregation
- Audits and reports all null actual_spend rows citing reasons from notes
- Prohibits silent formula assumptions (requires explicit --growth-type)
- Displays exact calculation formula in every output row
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple


def normalize_string(val: str) -> str:
    """Normalize whitespace and dashes for consistent matching."""
    return " ".join(val.replace("–", "-").replace("—", "-").split()).lower()


def load_dataset(file_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Load budget dataset, check headers, and audit all null actual_spend rows.
    Returns: (all_rows, null_rows)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget dataset not found: {file_path}")

    # Read with UTF-8, fallback to Latin-1 if needed
    encodings = ["utf-8-sig", "utf-8", "latin1"]
    content = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise ValueError("Failed to decode dataset with supported encodings.")

    reader = csv.DictReader(content.splitlines())
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required_cols:
        if col not in reader.fieldnames:
            raise ValueError(f"Missing required column in dataset: {col}")

    all_rows = list(reader)
    null_rows = [r for r in all_rows if not r["actual_spend"].strip()]

    return all_rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Compute granular per-period growth for a specific ward and category.
    Strictly refuses aggregation or missing growth_type.
    """
    # 1. Enforcement Check: Refusal of missing growth-type
    if not growth_type or growth_type.strip().upper() not in ["MOM", "YOY"]:
        raise ValueError(
            "REFUSAL: Growth type not specified or invalid. "
            "You must explicitly specify '--growth-type MoM' or '--growth-type YoY'. "
            "Silent formula assumption is prohibited."
        )

    # 2. Enforcement Check: Refusal of cross-ward or cross-category aggregation
    norm_ward = normalize_string(ward) if ward else ""
    norm_cat = normalize_string(category) if category else ""

    forbidden_aggregation = ["all", "total", "combined", "aggregate", "any", "citywide", ""]
    if norm_ward in forbidden_aggregation or not ward:
        raise ValueError(
            "REFUSAL: Aggregation across multiple wards is prohibited. "
            "You must specify a single, specific ward (e.g. 'Ward 1 – Kasba')."
        )
    if norm_cat in forbidden_aggregation or not category:
        raise ValueError(
            "REFUSAL: Aggregation across multiple categories is prohibited. "
            "You must specify a single, specific category (e.g. 'Roads & Pothole Repair')."
        )

    # Filter target rows
    filtered = [
        r
        for r in rows
        if norm_ward in normalize_string(r["ward"])
        and norm_cat in normalize_string(r["category"])
    ]

    if not filtered:
        raise ValueError(
            f"No matching records found for ward '{ward}' and category '{category}'."
        )

    # Sort sequentially by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    prev_period = None
    prev_spend = None

    for r in filtered:
        period = r["period"]
        budgeted = r["budgeted_amount"]
        raw_spend = r["actual_spend"].strip()
        notes = r["notes"].strip()

        if not raw_spend:
            growth_rate = "NULL"
            formula = f"Flagged null: {notes if notes else 'Missing value in source'}"
            current_spend = None
        else:
            current_spend = float(raw_spend)
            if prev_spend is None:
                if prev_period is None:
                    growth_rate = "N/A"
                    formula = f"Base period ({period}); no prior period available for MoM calculation"
                else:
                    growth_rate = "N/A"
                    formula = f"Prior period ({prev_period}) actual spend was NULL; base unavailable"
            else:
                pct = ((current_spend - prev_spend) / prev_spend) * 100
                growth_rate = f"{pct:+.1f}%"
                formula = (
                    f"(actual_spend[{period}] - actual_spend[{prev_period}]) / actual_spend[{prev_period}] * 100 = "
                    f"({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
                )

        results.append(
            {
                "period": period,
                "ward": r["ward"],
                "category": r["category"],
                "budgeted_amount": budgeted,
                "actual_spend": raw_spend if raw_spend else "NULL",
                "growth_type": growth_type.upper(),
                "growth_rate": growth_rate,
                "formula": formula,
                "notes": notes,
            }
        )

        prev_period = period
        prev_spend = current_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analytics")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth metric: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Load dataset and audit null rows
    try:
        all_rows, null_rows = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Dataset Audit: Loaded {len(all_rows)} total rows from {args.input}.")
    print(f"Dataset Audit: Found {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - [{nr['period']}] {nr['ward']} | {nr['category']} -> Reason: {nr['notes']}")

    # Check enforcement rules
    try:
        results = compute_growth(
            all_rows,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ValueError as err:
        print(f"\n{err}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "formula",
        "notes",
    ]

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSuccess: Computed {len(results)} rows for '{args.ward}' - '{args.category}'.")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
