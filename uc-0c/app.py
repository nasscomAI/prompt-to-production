"""
UC-0C app.py — Budget Growth Analytics.
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple


def normalize_str(s: str) -> str:
    """Normalize hyphens, dashes, and extra spaces for resilient matching."""
    if not s:
        return ""
    return s.replace("–", "-").replace("—", "-").strip().lower()


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Skill: load_dataset
    Reads CSV, validates schema, identifies and reports all null actual_spend rows.

    Returns:
        (rows, null_rows)
    """
    rows: List[Dict[str, str]] = []
    null_rows: List[Dict[str, str]] = []

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            raise ValueError(f"Input CSV missing required columns: {missing}")

        for line_num, row in enumerate(reader, start=2):
            actual = row.get("actual_spend", "").strip()
            if actual == "" or actual.lower() == "null":
                null_rows.append(row)
            rows.append(row)

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown
    and explicit null handling.
    """
    if not growth_type:
        raise ValueError("Growth type not specified. Refusing to guess. Please provide --growth-type (e.g. MoM).")

    if growth_type.upper() != "MOM":
        raise NotImplementedError(f"Growth type '{growth_type}' is not supported yet. Only 'MoM' is supported.")

    # Check for prohibited all-ward / all-category aggregation
    norm_ward = normalize_str(ward)
    norm_cat = normalize_str(category)
    if norm_ward in ["all", "any", "total", "combined"] or norm_cat in ["all", "any", "total", "combined"]:
        raise ValueError("Refusal: Cross-ward or cross-category aggregation is strictly prohibited to prevent false precision.")

    # Filter rows matching ward and category
    filtered = [
        r for r in rows
        if normalize_str(r["ward"]) == norm_ward and normalize_str(r["category"]) == norm_cat
    ]

    if not filtered:
        raise ValueError(f"No records found for ward '{ward}' and category '{category}'.")

    # Sort strictly by period
    filtered.sort(key=lambda x: x["period"])

    results: List[Dict[str, str]] = []
    prev_actual: Optional[float] = None
    prev_period: Optional[str] = None

    for r in filtered:
        period = r["period"]
        current_ward = r["ward"]
        current_cat = r["category"]
        actual_str = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        # Handle current null value
        if actual_str == "" or actual_str.lower() == "null":
            results.append({
                "period": period,
                "ward": current_ward,
                "category": current_cat,
                "actual_spend": "NULL",
                "previous_spend": f"{prev_actual:.1f}" if prev_actual is not None else "N/A",
                "growth_rate": "NULL",
                "formula": "N/A (actual spend is null)",
                "notes": notes or "Value is null",
                "flag": "NULL_VALUE",
            })
            prev_actual = None
            prev_period = period
            continue

        try:
            curr_val = float(actual_str)
        except ValueError:
            results.append({
                "period": period,
                "ward": current_ward,
                "category": current_cat,
                "actual_spend": actual_str,
                "previous_spend": f"{prev_actual:.1f}" if prev_actual is not None else "N/A",
                "growth_rate": "ERROR",
                "formula": "N/A (invalid float)",
                "notes": "Invalid numeric value",
                "flag": "INVALID_VALUE",
            })
            prev_actual = None
            prev_period = period
            continue

        # If this is the first period
        if prev_actual is None and prev_period is None:
            results.append({
                "period": period,
                "ward": current_ward,
                "category": current_cat,
                "actual_spend": f"{curr_val:.1f}",
                "previous_spend": "N/A",
                "growth_rate": "N/A",
                "formula": "N/A (first period in series)",
                "notes": notes,
                "flag": "",
            })
        elif prev_actual is None:
            # Previous period was NULL
            results.append({
                "period": period,
                "ward": current_ward,
                "category": current_cat,
                "actual_spend": f"{curr_val:.1f}",
                "previous_spend": "NULL",
                "growth_rate": "N/A",
                "formula": f"N/A (base period {prev_period} is null)",
                "notes": notes,
                "flag": "BASE_PERIOD_NULL",
            })
        else:
            # Calculate MoM growth
            growth = ((curr_val - prev_actual) / prev_actual) * 100
            sign = "+" if growth > 0 else ""
            formatted_growth = f"{sign}{growth:.1f}%"
            formula_str = f"({curr_val:.1f} - {prev_actual:.1f}) / {prev_actual:.1f} * 100 = {formatted_growth}"
            results.append({
                "period": period,
                "ward": current_ward,
                "category": current_cat,
                "actual_spend": f"{curr_val:.1f}",
                "previous_spend": f"{prev_actual:.1f}",
                "growth_rate": formatted_growth,
                "formula": formula_str,
                "notes": notes,
                "flag": "",
            })

        prev_actual = curr_val
        prev_period = period

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analytics")
    parser.add_argument("--input", required=True, help="Path to input ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to output growth CSV")
    parser.add_argument("--ward", required=False, default=None, help="Specific ward name")
    parser.add_argument("--category", required=False, default=None, help="Specific category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False, default=None, help="Growth metric (e.g. MoM)")
    args = parser.parse_args()

    # Rule: If growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print(
            "Error: --growth-type was not specified. Refusing to guess. Please provide --growth-type (e.g. MoM).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Rule: Never aggregate across wards or categories — require specific ward and category
    if not args.ward or not args.category:
        print(
            "Error: Both --ward and --category must be explicitly specified. Aggregating across wards/categories is prohibited.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        rows, null_rows = load_dataset(args.input)
        print(f"Loaded {len(rows)} rows. Detected {len(null_rows)} deliberate null actual_spend rows:")
        for nr in null_rows:
            print(f"  - {nr.get('period')} | {nr.get('ward')} | {nr.get('category')} | Note: {nr.get('notes')}")

        output_records = compute_growth(
            rows=rows,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )

        fieldnames = [
            "period",
            "ward",
            "category",
            "actual_spend",
            "previous_spend",
            "growth_rate",
            "formula",
            "notes",
            "flag",
        ]
        with open(args.output, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_records)

        print(f"Done. Growth table successfully written to {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

