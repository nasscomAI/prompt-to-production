"""
UC-0C — Budget Growth Calculator
"""
import argparse
import csv
import os
from typing import List, Optional


def load_dataset(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_spend(value: str) -> Optional[float]:
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return float(cleaned)


def compute_growth(rows: List[dict], ward: str, category: str, growth_type: str) -> List[dict]:
    if not ward or not category:
        raise ValueError("Ward and category are required.")
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("growth-type must be MoM or YoY.")
    if ward.lower() == "all" or category.lower() == "all":
        raise ValueError("Aggregation across all wards or categories is not allowed.")

    filtered = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    filtered.sort(key=lambda row: row["period"])

    results = []
    previous_value = None
    previous_period = None

    for row in filtered:
        current_value = parse_spend(row.get("actual_spend", ""))
        period = row["period"]
        if current_value is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_pct": "",
                    "formula": f"Not computed: null actual spend ({row.get('notes', 'no note')})",
                    "status": "FLAGGED_NULL",
                }
            )
            previous_value = None
            previous_period = period
            continue

        if previous_value is None or previous_value == 0:
            growth_pct = ""
            formula = "Not computed: no previous period value"
            status = "NO_BASE"
        else:
            if growth_type == "MoM":
                growth_pct_value = ((current_value - previous_value) / previous_value) * 100
            else:
                growth_pct_value = ((current_value - previous_value) / previous_value) * 100
            growth_pct = f"{growth_pct_value:+.1f}%"
            formula = f"(({current_value} - {previous_value}) / {previous_value}) * 100"
            status = "COMPUTED"

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value:.1f}",
                "growth_pct": growth_pct,
                "formula": formula,
                "status": status,
            }
        )

        previous_value = current_value
        previous_period = period

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward to analyse")
    parser.add_argument("--category", required=True, help="Category to analyse")
    parser.add_argument("--growth-type", default=None, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output")
    args = parser.parse_args()

    if not args.growth_type:
        print("Refusal: growth-type was not specified. Please provide MoM or YoY.")
        return

    rows = load_dataset(args.input)
    computed_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["period", "ward", "category", "actual_spend", "growth_pct", "formula", "status"])
        writer.writeheader()
        writer.writerows(computed_rows)

    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()
