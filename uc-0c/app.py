"""
UC-0C — Number That Looks Right
Budget Growth & Expenditure Analysis implementing RICE enforcement rules from agents.md and skills.md.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple, Optional, Any


def load_dataset(input_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Reads budget CSV dataset, validates required columns, and identifies all null actual_spend rows.
    Returns: (records, null_report)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Budget dataset file not found at: {input_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    records: List[Dict[str, Any]] = []
    null_report: List[Dict[str, Any]] = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required columns: {required_columns - set(reader.fieldnames or [])}")

        for row_idx, row in enumerate(reader, start=2):
            raw_spend = row["actual_spend"].strip() if row["actual_spend"] is not None else ""
            actual_spend: Optional[float] = None
            if raw_spend != "":
                try:
                    actual_spend = float(raw_spend)
                except ValueError:
                    actual_spend = None

            parsed_row = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": float(row["budgeted_amount"].strip()),
                "actual_spend": actual_spend,
                "notes": row.get("notes", "").strip(),
            }
            records.append(parsed_row)

            if actual_spend is None:
                null_report.append({
                    "row_index": row_idx,
                    "period": parsed_row["period"],
                    "ward": parsed_row["ward"],
                    "category": parsed_row["category"],
                    "budgeted_amount": parsed_row["budgeted_amount"],
                    "notes": parsed_row["notes"] or "Missing expenditure data",
                })

    return records, null_report


def compute_growth(
    records: List[Dict[str, Any]],
    ward_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    growth_type: str = "MoM",
) -> List[Dict[str, Any]]:
    """
    Computes growth strictly per-ward per-category without aggregating across groups.
    """
    if not growth_type:
        raise ValueError("REFUSAL: Growth type must be explicitly specified (e.g. --growth-type MoM).")

    if growth_type.upper() != "MOM":
        raise NotImplementedError(f"Growth calculation for '{growth_type}' is not supported. Supported: MoM")

    # Group records by (ward, category)
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for r in records:
        if ward_filter and ward_filter.upper() != "ALL" and r["ward"] != ward_filter:
            continue
        if category_filter and category_filter.upper() != "ALL" and r["category"] != category_filter:
            continue
        key = (r["ward"], r["category"])
        groups.setdefault(key, []).append(r)

    results: List[Dict[str, Any]] = []

    for (ward, category), items in groups.items():
        # Sort chronologically by period
        items.sort(key=lambda x: x["period"])

        prev_spend: Optional[float] = None
        for item in items:
            period = item["period"]
            budgeted = item["budgeted_amount"]
            curr_spend = item["actual_spend"]
            notes = item["notes"]

            if curr_spend is None:
                growth_pct = "N/A"
                formula = "Cannot compute: current period actual_spend is NULL"
                flag = "NULL_SPEND"
                out_spend_str = ""
            elif prev_spend is None:
                if items.index(item) == 0:
                    growth_pct = "N/A"
                    formula = "Baseline period: no prior period for MoM comparison"
                    flag = ""
                else:
                    growth_pct = "N/A"
                    formula = "Cannot compute: previous period actual_spend was NULL"
                    flag = "PRIOR_PERIOD_NULL"
                out_spend_str = f"{curr_spend:.1f}"
            else:
                if prev_spend == 0:
                    growth_pct = "N/A"
                    formula = "Undefined: division by zero (previous spend = 0)"
                    flag = "ZERO_DIVISION"
                else:
                    growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
                    sign = "+" if growth_val > 0 else ""
                    growth_pct = f"{sign}{growth_val:.1f}%"
                    formula = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
                    flag = ""
                out_spend_str = f"{curr_spend:.1f}"

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": out_spend_str,
                "growth_type": growth_type,
                "growth_pct": growth_pct,
                "formula": formula,
                "flag": flag,
                "notes": notes,
            })

            prev_spend = curr_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analyzer")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="Ward 1 – Kasba", help="Ward name or 'ALL'")
    parser.add_argument("--category", default="Roads & Pothole Repair", help="Category name or 'ALL'")
    parser.add_argument("--growth-type", default="MoM", help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--aggregate-all-wards", action="store_true", help="Flag that triggers refusal for cross-ward aggregation")
    parser.add_argument("--output", default="growth_output.csv", help="Path to output growth CSV")
    args = parser.parse_args()

    # Rule 1 Enforcement: Refuse cross-ward aggregation requests
    if args.aggregate_all_wards:
        print("REFUSAL: Cross-ward aggregation is strictly disallowed to prevent misleading data masking. Growth must be analyzed per-ward per-category.", file=sys.stderr)
        sys.exit(1)

    # Rule 4 Enforcement: Refuse if growth-type missing
    if not args.growth_type:
        print("REFUSAL: Growth type not specified. Please supply --growth-type (e.g. MoM).", file=sys.stderr)
        sys.exit(1)

    records, null_report = load_dataset(args.input)

    # Rule 2 Enforcement: Audit and display all null rows before computing
    print(f"=== PRE-COMPUTATION NULL AUDIT REPORT ({len(null_report)} null rows detected) ===")
    for n in null_report:
        print(f"  • Period: {n['period']} | Ward: {n['ward']} | Category: {n['category']} | Reason: {n['notes']}")
    print("=" * 70)

    results = compute_growth(
        records=records,
        ward_filter=args.ward,
        category_filter=args.category,
        growth_type=args.growth_type,
    )

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_pct",
        "formula",
        "flag",
        "notes",
    ]

    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Per-ward per-category growth table written to: {args.output}")


if __name__ == "__main__":
    main()

