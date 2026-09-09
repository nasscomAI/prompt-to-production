"""
UC-0C — Number That Looks Right
Ward-level budget growth calculator adhering to agents.md and skills.md.
Enforces granular per-ward analysis, flags nulls, and forbids silent aggregation.
"""
import argparse
import csv
import os
import sys


def load_dataset(file_path: str):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and null rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_rows = []

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            raise ValueError(f"Schema violation: missing columns {missing}")

        for idx, r in enumerate(reader, start=2):
            actual_val = r.get("actual_spend", "").strip()
            if actual_val == "" or actual_val.lower() in ("null", "none", "nan"):
                null_rows.append({
                    "line": idx,
                    "period": r.get("period"),
                    "ward": r.get("ward"),
                    "category": r.get("category"),
                    "notes": r.get("notes", "No notes provided")
                })
            rows.append(r)

    print(f"Dataset loaded: {len(rows)} rows. Detected {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - [{nr['period']}] {nr['ward']} | {nr['category']}: NULL (Reason: {nr['notes']})")

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str):
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses cross-ward aggregation and enforces strict formula application.
    """
    if not ward or ward.strip().lower() in ("all", "all wards", "total", "citywide", "*"):
        raise ValueError("REFUSAL: Aggregation across all wards is strictly prohibited by enforcement rules. A specific ward must be supplied.")

    if not category or category.strip().lower() in ("all", "all categories", "*"):
        raise ValueError("REFUSAL: Aggregation across all categories is strictly prohibited. A specific category must be supplied.")

    if not growth_type:
        raise ValueError("REFUSAL: --growth-type was not specified. You must choose MoM or YoY explicitly; guessing is forbidden.")

    if growth_type.upper() not in ("MOM", "YOY"):
        raise ValueError(f"REFUSAL: Unsupported growth type '{growth_type}'. Only MoM and YoY are supported.")

    # Filter rows matching ward and category
    filtered = [
        r for r in rows
        if r.get("ward", "").strip().lower() == ward.strip().lower()
        and r.get("category", "").strip().lower() == category.strip().lower()
    ]

    if not filtered:
        raise ValueError(f"No records found matching ward '{ward}' and category '{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda x: x.get("period", ""))

    output_rows = []
    prev_actual = None

    for r in filtered:
        period = r.get("period")
        b_amt = float(r.get("budgeted_amount", 0.0))
        raw_actual = r.get("actual_spend", "").strip()
        note = r.get("notes", "").strip()

        if raw_actual == "" or raw_actual.lower() in ("null", "none", "nan"):
            output_rows.append({
                "period": period,
                "ward": r.get("ward"),
                "category": r.get("category"),
                "budgeted_amount": f"{b_amt:.2f}",
                "actual_spend": "NULL",
                "growth_pct": "N/A",
                "formula": "None (Null spend row flagged)",
                "status": f"FLAGGED_NULL: {note}"
            })
            prev_actual = None
            continue

        act_val = float(raw_actual)
        if prev_actual is None:
            output_rows.append({
                "period": period,
                "ward": r.get("ward"),
                "category": r.get("category"),
                "budgeted_amount": f"{b_amt:.2f}",
                "actual_spend": f"{act_val:.2f}",
                "growth_pct": "N/A",
                "formula": "Baseline period — no previous period value available",
                "status": "BASELINE"
            })
        else:
            growth = ((act_val - prev_actual) / prev_actual) * 100.0
            sign = "+" if growth > 0 else ""
            formula_str = f"(({act_val:.1f} - {prev_actual:.1f}) / {prev_actual:.1f}) * 100"
            output_rows.append({
                "period": period,
                "ward": r.get("ward"),
                "category": r.get("category"),
                "budgeted_amount": f"{b_amt:.2f}",
                "actual_spend": f"{act_val:.2f}",
                "growth_pct": f"{sign}{growth:.1f}%",
                "formula": formula_str,
                "status": "COMPUTED"
            })
        prev_actual = act_val

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Target expenditure category")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY (guessing forbidden)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    try:
        rows, _ = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)

        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "period", "ward", "category", "budgeted_amount",
                "actual_spend", "growth_pct", "formula", "status"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Success: Growth calculations written to {args.output}")
    except Exception as e:
        print(f"Execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
