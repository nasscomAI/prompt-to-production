"""
UC-0C — Budget Growth Analytics (Number That Looks Right)
Built using RICE framework, agents.md guardrails, and skills.md specification.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Any, Optional, Tuple


def load_dataset(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Load CSV, audit all null rows, and return valid rows + null audit trail.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    rows = []
    null_rows = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            budgeted_str = row.get("budgeted_amount", "").strip()
            actual_str = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()

            budgeted = float(budgeted_str) if budgeted_str else 0.0
            actual = float(actual_str) if actual_str else None

            entry = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": notes,
            }
            rows.append(entry)

            if actual is None:
                null_rows.append(entry)

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
    output_path: str,
):
    """
    Calculate granular per-ward per-category growth and write to CSV.
    Refuses cross-ward aggregation and unstated formula choices.
    """
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(
            f"Invalid or missing --growth-type: '{growth_type}'. Must be explicitly 'MoM' or 'YoY'."
        )

    # Filter strictly for requested series
    series = [
        r for r in rows
        if r["ward"].lower() == ward.lower() and r["category"].lower() == category.lower()
    ]

    if not series:
        raise ValueError(
            f"No data found for Ward: '{ward}' and Category: '{category}'"
        )

    # Sort deterministically by period
    series.sort(key=lambda x: x["period"])

    output_rows = []
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_pct",
        "formula",
        "status",
        "notes",
    ]

    for i, current in enumerate(series):
        actual_curr = current["actual_spend"]
        period_curr = current["period"]
        notes_curr = current["notes"]

        if i == 0:
            output_rows.append({
                "period": period_curr,
                "ward": current["ward"],
                "category": current["category"],
                "budgeted_amount": current["budgeted_amount"],
                "actual_spend": actual_curr if actual_curr is not None else "",
                "growth_type": growth_type,
                "growth_pct": "N/A",
                "formula": "Baseline (First period in series)",
                "status": "BASELINE" if actual_curr is not None else "NULL_VALUE",
                "notes": notes_curr,
            })
            continue

        prev = series[i - 1]
        actual_prev = prev["actual_spend"]

        if actual_curr is None:
            output_rows.append({
                "period": period_curr,
                "ward": current["ward"],
                "category": current["category"],
                "budgeted_amount": current["budgeted_amount"],
                "actual_spend": "",
                "growth_type": growth_type,
                "growth_pct": "N/A",
                "formula": f"({growth_type}: actual_current is NULL)",
                "status": "NULL_VALUE",
                "notes": notes_curr or f"Missing actual_spend in {period_curr}",
            })
        elif actual_prev is None:
            output_rows.append({
                "period": period_curr,
                "ward": current["ward"],
                "category": current["category"],
                "budgeted_amount": current["budgeted_amount"],
                "actual_spend": actual_curr,
                "growth_type": growth_type,
                "growth_pct": "N/A",
                "formula": f"({growth_type}: previous period {prev['period']} was NULL)",
                "status": "NULL_PREV_PERIOD",
                "notes": f"Cannot compute growth: prior period {prev['period']} is NULL",
            })
        else:
            diff = actual_curr - actual_prev
            growth_val = (diff / actual_prev) * 100.0
            sign = "+" if growth_val > 0 else ""
            growth_formatted = f"{sign}{growth_val:.1f}%"
            formula_str = f"(({actual_curr:.1f} - {actual_prev:.1f}) / {actual_prev:.1f}) * 100"

            output_rows.append({
                "period": period_curr,
                "ward": current["ward"],
                "category": current["category"],
                "budgeted_amount": current["budgeted_amount"],
                "actual_spend": actual_curr,
                "growth_type": growth_type,
                "growth_pct": growth_formatted,
                "formula": formula_str,
                "status": "COMPUTED",
                "notes": notes_curr,
            })

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analytics")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth calculation type")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: Refuse cross-ward aggregation
    if args.ward.lower() in ["all", "all wards", "total", "aggregate", "combined"]:
        sys.stderr.write(
            "REFUSAL: Cross-ward aggregation is strictly prohibited by RICE enforcement rules. "
            "Please specify an individual ward.\n"
        )
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)
    print(f"Loaded dataset: {len(rows)} rows total.")
    print(f"Audited {len(null_rows)} NULL actual_spend rows:")
    for nr in null_rows:
        print(f"  - {nr['period']} · {nr['ward']} · {nr['category']} (Notes: {nr['notes']})")

    compute_growth(
        rows=rows,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
        output_path=args.output,
    )
    print(f"Results successfully written to: {args.output}")


if __name__ == "__main__":
    main()
