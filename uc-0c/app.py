"""
UC-0C — Number That Looks Right
Budget growth calculator with strict aggregation refusal and null flagging.
Guided by agents.md and skills.md.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Optional, Tuple


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Read budget CSV, validate columns, and detect null actual_spend rows.
    Returns: (all_rows, null_rows)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    all_rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns in dataset: {missing}")

        for row in reader:
            all_rows.append(row)
            actual_spend = row.get("actual_spend", "").strip()
            if not actual_spend:
                null_rows.append(row)

    print(f"Dataset loaded: {len(all_rows)} total rows, {len(null_rows)} null actual_spend rows detected:")
    for nr in null_rows:
        print(f"  - {nr['period']} · {nr['ward']} · {nr['category']} | Reason: {nr.get('notes', 'No note provided')}")

    return all_rows, null_rows


def compute_growth(
    dataset: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Compute growth per period for a specific ward and category.
    Refuses cross-ward aggregation and missing growth_type.
    Flags null records and exposes computation formulas.
    """
    # Enforcement 1: Refuse cross-ward or cross-category aggregation
    if not ward or ward.lower() in ["all", "any", "total", "all wards", "all-ward"]:
        raise ValueError("REFUSAL: Cross-ward aggregation is strictly prohibited. You must specify a single ward.")
    if not category or category.lower() in ["all", "any", "total", "all categories"]:
        raise ValueError("REFUSAL: Cross-category aggregation is strictly prohibited. You must specify a single category.")

    # Enforcement 4: If growth_type not specified, refuse
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError(
            f"REFUSAL: Invalid or missing growth type '{growth_type}'. "
            "System will not guess default. Please explicitly specify 'MoM' or 'YoY'."
        )

    # Filter rows for target ward and category
    filtered = [
        r for r in dataset
        if r["ward"].strip().lower() == ward.strip().lower()
        and r["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered:
        raise ValueError(f"No records found for ward='{ward}' and category='{category}'")

    # Sort chronologically by period
    filtered.sort(key=lambda r: r["period"])

    output_rows = []
    prev_spend: Optional[float] = None
    prev_period: Optional[str] = None

    for i, row in enumerate(filtered):
        period = row["period"]
        budgeted = row.get("budgeted_amount", "")
        spend_str = row.get("actual_spend", "").strip()
        data_note = row.get("notes", "").strip()

        # Check for deliberate null
        if not spend_str:
            output_rows.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "growth_type": growth_type.upper(),
                "growth_rate": "NULL",
                "formula": "Cannot compute: actual_spend is null",
                "notes": data_note or "Data missing/unreported",
            })
            prev_spend = None
            prev_period = period
            continue

        try:
            current_spend = float(spend_str)
        except ValueError:
            output_rows.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": spend_str,
                "growth_type": growth_type.upper(),
                "growth_rate": "NULL",
                "formula": "Cannot compute: invalid numeric value",
                "notes": f"Invalid number: {spend_str}",
            })
            prev_spend = None
            prev_period = period
            continue

        if i == 0 or prev_spend is None:
            formula_desc = "Baseline period (no prior comparison period available)" if i == 0 else f"Cannot compute: prior period ({prev_period}) spend was null"
            output_rows.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": f"{current_spend:.1f}",
                "growth_type": growth_type.upper(),
                "growth_rate": "N/A" if i == 0 else "NULL",
                "formula": formula_desc,
                "notes": data_note,
            })
        else:
            # MoM calculation
            rate = ((current_spend - prev_spend) / prev_spend) * 100
            sign = "+" if rate >= 0 else ""
            growth_str = f"{sign}{rate:.1f}%"
            formula_str = f"(({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"

            output_rows.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": f"{current_spend:.1f}",
                "growth_type": growth_type.upper(),
                "growth_rate": growth_str,
                "formula": formula_str,
                "notes": data_note,
            })

        prev_spend = current_spend
        prev_period = period

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific expenditure category")
    parser.add_argument("--growth-type", dest="growth_type", required=False, default=None, help="Growth type: 'MoM' or 'YoY'")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Rule 4: If growth_type not specified, refuse and ask
    if not args.growth_type:
        print("ERROR: --growth-type must be specified ('MoM' or 'YoY'). System refuses to assume a default.", file=sys.stderr)
        sys.exit(1)

    dataset, null_rows = load_dataset(args.input)

    try:
        results = compute_growth(
            dataset=dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ValueError as e:
        print(f"EXECUTION REFUSED: {e}", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

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

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth calculation complete. Output written to {args.output}")


if __name__ == "__main__":
    main()
