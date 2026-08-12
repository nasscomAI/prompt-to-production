"""
UC-0C — Number That Looks Right
Calculates MoM budget spend growth per-ward per-category, refusing global aggregations and flagging null values.
"""
import argparse
import csv
import sys
import os
from typing import List, Dict, Tuple


def load_dataset(file_path: str) -> Tuple[List[dict], List[dict]]:
    """
    Reads CSV file, parses numbers, and identifies rows with null actual_spend.
    Returns (rows, null_rows).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    rows = []
    null_rows = []

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_spend = r.get("actual_spend", "").strip()
            parsed_row = {
                "period": r.get("period", "").strip(),
                "ward": r.get("ward", "").strip(),
                "category": r.get("category", "").strip(),
                "budgeted_amount": float(r.get("budgeted_amount", 0.0)) if r.get("budgeted_amount") else 0.0,
                "actual_spend": float(raw_spend) if raw_spend != "" else None,
                "notes": r.get("notes", "").strip()
            }
            rows.append(parsed_row)
            if parsed_row["actual_spend"] is None:
                null_rows.append(parsed_row)

    return rows, null_rows


def compute_growth(rows: List[dict], ward: str, category: str, growth_type: str = "MoM") -> List[dict]:
    """
    Computes MoM growth for specified ward and category.
    Refuses global aggregations and flags null spend values.
    """
    # Enforcement: Refuse all-ward or all-category global aggregation
    if not ward or ward.lower() in ["all", "global", "any", "total"] or not category or category.lower() in ["all", "global", "any", "total"]:
        print("ERROR [REFUSAL]: All-ward or all-category global aggregation is strictly prohibited. You must specify an explicit ward and category.")
        sys.exit(1)

    filtered = [r for r in rows if r["ward"].lower() == ward.lower() and r["category"].lower() == category.lower()]
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend = None

    for r in filtered:
        curr_spend = r["actual_spend"]
        note = r["notes"]

        if curr_spend is None:
            mom_growth_str = "NULL (Flagged)"
            if not note:
                note = "Missing actual_spend value"
        elif prev_spend is None:
            mom_growth_str = "N/A"
        else:
            pct = ((curr_spend - prev_spend) / prev_spend) * 100.0
            sign = "+" if pct > 0 else ""
            mom_growth_str = f"{sign}{pct:.1f}%"

        results.append({
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": curr_spend if curr_spend is not None else "NULL",
            "mom_growth": mom_growth_str,
            "notes": note
        })

        if curr_spend is not None:
            prev_spend = curr_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", default="MoM", help="Growth metric (MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

