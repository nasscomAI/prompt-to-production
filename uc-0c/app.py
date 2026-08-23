"""
UC-0C app.py — Ward Budget Growth Calculator
Build this using the RICE + agents.md + skills.md workflow.
See README.md for run command and expected behaviour.
Imthiaz Ahmed
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple, Optional


def load_dataset(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Reads the budget CSV dataset, validates required columns, inspects null `actual_spend` values,
    and reports null count and affected rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
    rows = []
    null_report = []

    with open(file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns in dataset: {missing}")

        for line_num, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.lower() in ["null", "none", "nan"]:
                actual_spend = None
                null_report.append({
                    "line": line_num,
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", "")
                })
            else:
                try:
                    actual_spend = float(raw_spend)
                except ValueError:
                    actual_spend = None
                    null_report.append({
                        "line": line_num,
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "notes": row.get("notes", f"Unparseable spend value '{raw_spend}'")
                    })

            try:
                budgeted_amount = float(row.get("budgeted_amount", 0.0))
            except ValueError:
                budgeted_amount = 0.0

            rows.append({
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": row.get("notes", "").strip()
            })

    print(f"[INFO] Dataset loaded successfully: {len(rows)} total rows.")
    print(f"[INFO] Null inspection: {len(null_report)} null actual_spend rows detected.")
    for nr in null_report:
        print(f"  - Null at {nr['period']} | {nr['ward']} | {nr['category']} -> Notes: '{nr['notes']}'")

    return rows, null_report


def compute_growth(data: List[Dict], ward: Optional[str], category: Optional[str], growth_type: Optional[str]) -> List[Dict]:
    """
    Calculates per-period budget spend growth for a specific ward and category based on
    the specified growth type (MoM or YoY), including explicit formulas and null flags.
    Refuses cross-ward/cross-category aggregation or missing growth_type.
    """
    # 1. Enforcement Rule: Check for missing or aggregation requests
    if not ward or ward.strip().lower() in ["all", "any", "aggregated", "*"]:
        raise ValueError("REFUSAL: Cross-ward aggregation is strictly prohibited. You must specify a single specific ward.")

    if not category or category.strip().lower() in ["all", "any", "aggregated", "*"]:
        raise ValueError("REFUSAL: Cross-category aggregation is strictly prohibited. You must specify a single specific category.")

    if not growth_type or growth_type.strip().upper() not in ["MOM", "YOY"]:
        raise ValueError("REFUSAL: Growth type must be explicitly specified (e.g. --growth-type MoM or --growth-type YoY). System will not guess formula.")

    g_type = growth_type.strip().upper()
    target_ward = ward.strip()
    target_category = category.strip()

    subset = [r for r in data if r["ward"].lower() == target_ward.lower() and r["category"].lower() == target_category.lower()]

    if not subset:
        raise ValueError(f"No records found matching ward '{target_ward}' and category '{target_category}'.")

    subset.sort(key=lambda x: x["period"])

    results = []
    period_map = {r["period"]: r for r in subset}

    for i, row in enumerate(subset):
        period = row["period"]
        spend_curr = row["actual_spend"]
        budgeted = row["budgeted_amount"]
        notes = row["notes"]

        if g_type == "MOM":
            formula_str = "MoM Growth = ((Spend_t - Spend_{t-1}) / Spend_{t-1}) * 100"
            if i == 0:
                growth_pct_str = "N/A (First period)"
                notes_out = notes if notes else "First period in dataset"
            else:
                prev_row = subset[i - 1]
                spend_prev = prev_row["actual_spend"]
                if spend_curr is None:
                    growth_pct_str = "NULL"
                    notes_out = f"FLAGGED: Current period spend is NULL. Reason: {notes}" if notes else "FLAGGED: Current period spend is NULL."
                elif spend_prev is None:
                    growth_pct_str = "NULL"
                    notes_out = f"FLAGGED: Prior period ({prev_row['period']}) spend was NULL."
                elif spend_prev == 0:
                    growth_pct_str = "N/A (Divide by zero)"
                    notes_out = notes
                else:
                    pct = ((spend_curr - spend_prev) / spend_prev) * 100
                    sign = "+" if pct > 0 else ""
                    growth_pct_str = f"{sign}{pct:.1f}%"
                    notes_out = notes

        elif g_type == "YOY":
            formula_str = "YoY Growth = ((Spend_t - Spend_{t-12}) / Spend_{t-12}) * 100"
            parts = period.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                yr, mo = int(parts[0]), int(parts[1])
                prev_period = f"{yr - 1:04d}-{mo:02d}"
                prev_row = period_map.get(prev_period)

                if prev_row is None:
                    growth_pct_str = "N/A (Prior year period not in dataset)"
                    notes_out = notes if notes else "Prior year baseline unavailable"
                elif spend_curr is None:
                    growth_pct_str = "NULL"
                    notes_out = f"FLAGGED: Current period spend is NULL. Reason: {notes}" if notes else "FLAGGED: Current period spend is NULL."
                elif prev_row["actual_spend"] is None:
                    growth_pct_str = "NULL"
                    notes_out = f"FLAGGED: Prior year period ({prev_period}) spend was NULL."
                elif prev_row["actual_spend"] == 0:
                    growth_pct_str = "N/A (Divide by zero)"
                    notes_out = notes
                else:
                    spend_prev = prev_row["actual_spend"]
                    pct = ((spend_curr - spend_prev) / spend_prev) * 100
                    sign = "+" if pct > 0 else ""
                    growth_pct_str = f"{sign}{pct:.1f}%"
                    notes_out = notes
            else:
                growth_pct_str = "N/A"
                notes_out = notes

        spend_str = f"{spend_curr:.1f}" if spend_curr is not None else "NULL"
        budget_str = f"{budgeted:.1f}"

        results.append({
            "ward": row["ward"],
            "category": row["category"],
            "period": period,
            "budgeted_amount": budget_str,
            "actual_spend": spend_str,
            "growth_pct": growth_pct_str,
            "formula_used": formula_str,
            "notes": notes_out
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input ward budget CSV file")
    parser.add_argument("--ward", required=False, default=None, help="Specific ward name")
    parser.add_argument("--category", required=False, default=None, help="Specific category name")
    parser.add_argument("--growth-type", required=False, default=None, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output growth CSV file")

    args = parser.parse_args()

    try:
        data, null_report = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as ve:
        print(f"\n[EXECUTION ERROR / REFUSAL]\n{str(ve)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR]\n{str(e)}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["ward", "category", "period", "budgeted_amount", "actual_spend", "growth_pct", "formula_used", "notes"]

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[SUCCESS] Calculated growth for '{args.ward}' | '{args.category}' ({args.growth_type}).")
    print(f"Results successfully written to {args.output}")


if __name__ == "__main__":
    main()

