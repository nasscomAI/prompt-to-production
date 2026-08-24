#!/usr/bin/env python3
"""
UC-0C: Ward Budget Growth Calculator
Computes per-ward per-category growth rates with explicit null handling.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ["MoM", "YoY"]


class AggregationRefusedError(Exception):
    pass


class ParseError(Exception):
    pass


def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Reads ward_budget.csv, validates required columns, and reports null count
    with specific row details before returning structured data.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    rows = []
    null_report = []

    try:
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ParseError("CSV file is empty or has no headers")

            missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            for line_num, row in enumerate(reader, start=2):
                actual_spend_raw = row.get("actual_spend", "").strip()
                is_null = actual_spend_raw == ""

                processed_row = {
                    "period": row["period"].strip(),
                    "ward": row["ward"].strip(),
                    "category": row["category"].strip(),
                    "budgeted_amount": float(row["budgeted_amount"]) if row["budgeted_amount"] else 0.0,
                    "actual_spend": float(actual_spend_raw) if not is_null else None,
                    "notes": row["notes"].strip(),
                }
                rows.append(processed_row)

                if is_null:
                    null_report.append({
                        "period": processed_row["period"],
                        "ward": processed_row["ward"],
                        "category": processed_row["category"],
                        "reason": processed_row["notes"] or "No reason provided"
                    })

    except csv.Error as e:
        raise ParseError(f"CSV parse error at line {line_num}: {e}")

    return {
        "rows": rows,
        "null_report": null_report,
        "column_validation": True
    }


def compute_growth(
    rows: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
    output_path: str
) -> List[Dict[str, Any]]:
    """
    Computes per-period growth for a specific ward+category+growth_type,
    returning a table with formula shown per row.
    """
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"Invalid growth_type: '{growth_type}'. Must be one of: {VALID_GROWTH_TYPES}. Never guess — specify explicitly.")

    ward_rows = [r for r in rows if r["ward"] == ward]
    if not ward_rows:
        available_wards = sorted(set(r["ward"] for r in rows))
        raise ValueError(f"Ward '{ward}' not found. Available wards: {available_wards}")

    category_rows = [r for r in ward_rows if r["category"] == category]
    if not category_rows:
        available_categories = sorted(set(r["category"] for r in ward_rows))
        raise ValueError(f"Category '{category}' not found for ward '{ward}'. Available categories: {available_categories}")

    category_rows.sort(key=lambda r: r["period"])

    output_rows = []

    for i, row in enumerate(category_rows):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]

        if actual_spend is None:
            output_rows.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula_used": "N/A — null actual_spend",
                "null_flag": True,
                "null_reason": notes or "No reason provided"
            })
            continue

        null_flag = False
        null_reason = ""
        formula_used = ""
        growth_pct = "NULL"

        if growth_type == "MoM":
            if i == 0:
                formula_used = "N/A — first period (no prior month)"
                growth_pct = "NULL"
            else:
                prev_spend = category_rows[i - 1]["actual_spend"]
                if prev_spend is None:
                    formula_used = f"({actual_spend} - NULL) / NULL — prior month actual_spend is null"
                    growth_pct = "NULL"
                    null_flag = True
                    null_reason = category_rows[i - 1]["notes"] or "Prior month null"
                else:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    growth_pct = f"{growth:+.1f}%"
                    formula_used = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100 = {growth:+.1f}%"

        elif growth_type == "YoY":
            formula_used = "N/A — YoY requires prior year data (not available in 2024-only dataset)"
            growth_pct = "NULL"

        output_rows.append({
            "period": period,
            "actual_spend": f"{actual_spend:.1f}",
            "growth_pct": growth_pct,
            "formula_used": formula_used,
            "null_flag": null_flag,
            "null_reason": null_reason
        })

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["period", "actual_spend", "growth_pct", "formula_used", "null_flag", "null_reason"]
    with output_path_obj.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=VALID_GROWTH_TYPES, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)

        if dataset["null_report"]:
            print(f"Null rows detected ({len(dataset['null_report'])}):", file=sys.stderr)
            for nr in dataset["null_report"]:
                print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}", file=sys.stderr)

        compute_growth(
            rows=dataset["rows"],
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
            output_path=args.output
        )

        print(f"Growth table written to: {args.output}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except AggregationRefusedError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()