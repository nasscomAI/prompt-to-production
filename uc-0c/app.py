"""
UC-0C — Number That Looks Right
RICE + agents.md + skills.md + CRAFT implementation.
"""
import argparse
import csv
import sys
from typing import Dict, List, Optional


def load_dataset(input_path: str) -> List[dict]:
    """
    Read CSV budget dataset, validate schema, handle null actual_spend rows.
    """
    records = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.upper() == "NULL":
                spend_val = None
            else:
                spend_val = float(raw_spend)

            records.append({
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": float(row.get("budgeted_amount", 0.0)),
                "actual_spend": spend_val,
                "notes": row.get("notes", "").strip(),
            })
    return records


def compute_growth(
    records: List[dict], ward: str, category: str, growth_type: str
) -> List[dict]:
    """
    Compute growth per period for a specific ward and category.
    Includes explicit formulas in every row and flags null rows.
    """
    # Filter matching ward and category
    filtered = [
        r for r in records if r["ward"] == ward and r["category"] == category
    ]
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend: Optional[float] = None

    for i, rec in enumerate(filtered):
        period = rec["period"]
        curr_spend = rec["actual_spend"]
        budgeted = rec["budgeted_amount"]
        notes = rec["notes"]

        if growth_type == "MoM":
            formula_str = "((actual_spend_t - actual_spend_t-1) / actual_spend_t-1) * 100"
        elif growth_type == "YoY":
            formula_str = "((actual_spend_t - actual_spend_t-12) / actual_spend_t-12) * 100"
        else:
            formula_str = "Unknown"

        # Check if current month spend is NULL
        if curr_spend is None:
            growth_rate = "NULL"
            note_out = f"FLAGGED: {notes}" if notes else "FLAGGED: Null actual spend"
        elif i == 0:
            growth_rate = "N/A (First Period)"
            note_out = notes
        elif prev_spend is None:
            growth_rate = "N/A (Previous period NULL)"
            note_out = f"Previous period spend was NULL. {notes}".strip()
        else:
            diff = curr_spend - prev_spend
            pct = (diff / prev_spend) * 100.0
            sign = "+" if pct > 0 else ""
            growth_rate = f"{sign}{pct:.1f}%"
            note_out = notes

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": curr_spend if curr_spend is not None else "NULL",
            "growth_type": growth_type,
            "growth_rate": growth_rate,
            "formula": formula_str,
            "notes": note_out,
        })

        prev_spend = curr_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, choices=["MoM", "YoY"], help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    # Refusal Check 1: --growth-type must be specified explicitly
    if not args.growth_type:
        sys.stderr.write("REFUSAL ERROR: --growth-type (MoM or YoY) must be explicitly specified. System will not guess formula.\n")
        sys.exit(1)

    # Refusal Check 2: Ward and Category must be specified (No all-ward / global aggregation)
    if not args.ward or args.ward.upper() == "ALL":
        sys.stderr.write("REFUSAL ERROR: Global / all-ward aggregation is strictly prohibited. You must specify a specific --ward.\n")
        sys.exit(1)

    if not args.category or args.category.upper() == "ALL":
        sys.stderr.write("REFUSAL ERROR: Category aggregation across all categories is prohibited. You must specify a specific --category.\n")
        sys.exit(1)

    records = load_dataset(args.input)
    growth_results = compute_growth(records, args.ward, args.category, args.growth_type)

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
        writer.writerows(growth_results)

    print(f"Growth calculation written to {args.output}")


if __name__ == "__main__":
    main()

