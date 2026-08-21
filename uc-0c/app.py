"""
UC-0C — Number That Looks Right
Per-ward, per-category budget growth computation adhering strictly to RICE specifications.
"""
import argparse
import csv
import os
import sys

VALID_GROWTH_TYPES = ["MoM", "YoY"]

def load_dataset(file_path: str):
    """
    Reads CSV, validates required columns, detects and reports null actual_spend rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input budget file not found: {file_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_rows = []

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Missing required columns. Expected {required_cols}, found {reader.fieldnames}")

        for idx, row in enumerate(reader, start=2):
            rows.append(row)
            actual_str = row.get("actual_spend", "").strip()
            if not actual_str:
                null_rows.append({
                    "row_index": idx,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes", "No notes provided")
                })

    print(f"Loaded {len(rows)} rows from dataset.")
    print(f"Detected {len(null_rows)} null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Row {nr['row_index']} ({nr['period']} · {nr['ward']} · {nr['category']}): {nr['notes']}")

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes per-period growth rate for a specific ward and category without aggregation.
    Refuses silent guessing, multi-ward aggregation, or missing formulas.
    """
    if not growth_type or growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Growth type '{growth_type}' is invalid or missing. Must be explicitly one of: {VALID_GROWTH_TYPES}. Refusing to guess."
        )

    if not ward or ward.lower() in ("all", "any", "total", "overall"):
        raise ValueError(
            "Refusal: Cross-ward aggregation is strictly forbidden by policy. A specific single ward must be specified."
        )

    if not category or category.lower() in ("all", "any", "total", "overall"):
        raise ValueError(
            "Refusal: Cross-category aggregation is strictly forbidden by policy. A specific single category must be specified."
        )

    # Filter strictly for the requested ward and category
    filtered = [
        r for r in rows
        if r.get("ward", "").strip() == ward.strip() and r.get("category", "").strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda x: x.get("period", ""))

    results = []
    prev_spend = None

    for idx, r in enumerate(filtered):
        period = r.get("period", "")
        budget = r.get("budgeted_amount", "")
        act_str = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        if not act_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": "NULL",
                "growth_type": growth_type,
                "growth_rate": "N/A",
                "formula_used": "N/A (Actual spend is NULL)",
                "status_flag": "FLAGGED_NULL",
                "notes": notes or "Data missing in source record"
            })
            prev_spend = None
            continue

        try:
            curr_spend = float(act_str)
        except ValueError:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": act_str,
                "growth_type": growth_type,
                "growth_rate": "N/A",
                "formula_used": "N/A (Non-numeric value)",
                "status_flag": "FLAGGED_INVALID",
                "notes": f"Invalid number: {act_str}"
            })
            prev_spend = None
            continue

        if prev_spend is None:
            if idx == 0:
                growth_str = "N/A"
                formula_str = "Baseline period — no prior period data"
            else:
                growth_str = "N/A"
                formula_str = "Prior period was NULL or invalid"
            status_flag = "VALID"
        else:
            growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
            growth_str = f"{growth_val:+.1f}%"
            formula_str = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
            status_flag = "VALID"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budget,
            "actual_spend": f"{curr_spend:.1f}",
            "growth_type": growth_type,
            "growth_rate": growth_str,
            "formula_used": formula_str,
            "status_flag": status_flag,
            "notes": notes
        })
        prev_spend = curr_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Budget category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output path for growth_output.csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "formula_used",
        "status_flag",
        "notes"
    ]

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Computed {len(results)} period rows written to {args.output}")


if __name__ == "__main__":
    main()
