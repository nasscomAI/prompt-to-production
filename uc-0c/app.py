"""
UC-0C — Budget Growth Calculator

Implements RICE rules from agents.md and skills from skills.md:
- load_dataset: Loads ward_budget.csv and identifies deliberate null rows.
- compute_growth: Computes per-period growth with explicit formula display
  and flags null values with their recorded reasons without silent aggregations.
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
AGGREGATION_TOKENS = {"all", "*", "any", "total", "combined", ""}


def _is_aggregation_request(value: str) -> bool:
    return (value or "").strip().lower() in AGGREGATION_TOKENS


def load_dataset(input_path: str):
    """Load CSV, validate schema, and return rows plus all null actual_spend rows."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"Required columns missing from CSV: {missing}")

    null_rows = [
        {
            "period": r.get("period", ""),
            "ward": r.get("ward", ""),
            "category": r.get("category", ""),
            "notes": (r.get("notes") or "").strip(),
        }
        for r in rows
        if not r.get("actual_spend") or (r.get("actual_spend") or "").strip() == ""
    ]
    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Compute period-over-period growth for a specific ward and category."""
    if not growth_type:
        raise ValueError("Error: --growth-type must be explicitly provided (e.g. 'MoM'). Refusing to assume formula silently.")

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Growth type '{growth_type}' is not supported. "
            "Only 'MoM' can be computed (dataset covers a single year, 2024). "
            "Refusing to guess a formula."
        )

    if _is_aggregation_request(ward) or _is_aggregation_request(category):
        raise ValueError(
            f"REFUSED: all-ward / multi-category aggregation (ward='{ward}', category='{category}') "
            "is not allowed. Provide a single specific ward and category."
        )

    # Filter strictly for requested ward and category (no unauthorized cross-ward aggregation)
    filtered = [
        r for r in rows
        if r.get("ward", "").strip() == ward.strip() and r.get("category", "").strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(f"No records found for ward='{ward}' and category='{category}'")

    # Sort by period
    filtered.sort(key=lambda x: x.get("period", ""))

    results = []
    prev_spend = None

    for r in filtered:
        period = r.get("period", "")
        b_amount = r.get("budgeted_amount", "")
        spend_str = (r.get("actual_spend") or "").strip()
        notes = (r.get("notes") or "").strip()

        if spend_str == "":
            curr_spend = None
            growth_pct = "NULL"
            formula = "N/A (actual_spend is NULL)"
            flag = "FLAGGED_NULL"
            row_notes = notes if notes else "Deliberate null in dataset"
        else:
            try:
                curr_spend = float(spend_str)
            except ValueError:
                curr_spend = None
                growth_pct = "ERROR"
                formula = "Invalid numeric value"
                flag = "INVALID_NUMBER"
                row_notes = notes

            if curr_spend is not None:
                if prev_spend is None:
                    growth_pct = "N/A (baseline)"
                    formula = "N/A (first available period)"
                    flag = ""
                    row_notes = notes
                else:
                    growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
                    growth_pct = f"{growth_val:+.1f}%"
                    formula = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
                    flag = ""
                    row_notes = notes

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": b_amount,
            "actual_spend": spend_str if spend_str != "" else "NULL",
            "growth_type": growth_type,
            "growth_pct": growth_pct,
            "formula": formula,
            "flag": flag,
            "notes": row_notes,
        })

        if curr_spend is not None:
            prev_spend = curr_spend
        else:
            prev_spend = None  # Cannot compute next MoM if current base is missing

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g. 'MoM')")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    print(f"Loaded {len(rows)} records. Found {len(null_rows)} total null actual_spend rows across dataset:")
    for n in null_rows:
        reason = n["notes"] or "(no reason recorded)"
        print(f"  - {n['period']} | {n['ward']} | {n['category']} | reason: {reason}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    flagged = [r for r in results if r["flag"]]
    print(f"Computed MoM growth for ward='{args.ward}', category='{args.category}' "
          f"({len(results)} periods, {len(flagged)} flagged rows).")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "period", "ward", "category", "budgeted_amount", "actual_spend",
            "growth_type", "growth_pct", "formula", "flag", "notes"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth analysis written to {args.output}")


if __name__ == "__main__":
    main()
