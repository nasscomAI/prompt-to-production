"""
UC-0C — Number That Looks Right (Ward Budget Growth Calculator)
Deterministic growth calculator based on uc-0c/agents.md and uc-0c/skills.md.
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

DISALLOWED_AGGREGATIONS = {
    "all",
    "all wards",
    "all categories",
    "any",
    "*",
    "total",
    "city",
    "city-wide",
    "cross-ward",
    "cross-category",
}


def load_dataset(file_path: str):
    """
    Reads and validates ward_budget.csv.
    Audits and reports all NULL actual_spend rows without zero-imputation.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: '{file_path}'")

    rows = []
    null_rows = []

    with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        
        # Validate column headers
        if not reader.fieldnames:
            raise ValueError(f"File '{file_path}' is empty or missing headers.")
        
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        for line_num, r in enumerate(reader, start=2):
            raw_spend = r.get("actual_spend", "").strip()
            
            # Preserve NULL without zero-imputation
            if raw_spend == "" or raw_spend.upper() == "NULL":
                spend_val = None
                null_rows.append({
                    "line": line_num,
                    "period": r.get("period", ""),
                    "ward": r.get("ward", ""),
                    "category": r.get("category", ""),
                    "notes": r.get("notes", ""),
                })
            else:
                try:
                    spend_val = float(raw_spend)
                except ValueError:
                    spend_val = None
                    null_rows.append({
                        "line": line_num,
                        "period": r.get("period", ""),
                        "ward": r.get("ward", ""),
                        "category": r.get("category", ""),
                        "notes": f"Invalid numeric format: '{raw_spend}'",
                    })

            cleaned_row = {
                "period": r.get("period", "").strip(),
                "ward": r.get("ward", "").strip(),
                "category": r.get("category", "").strip(),
                "budgeted_amount": r.get("budgeted_amount", "").strip(),
                "actual_spend": spend_val,
                "notes": r.get("notes", "").strip(),
            }
            rows.append(cleaned_row)

    # Print explicit null audit report
    print("=" * 70)
    print("DATASET AUDIT REPORT")
    print("=" * 70)
    print(f"Total Rows Ingested: {len(rows)}")
    print(f"Deliberate NULL actual_spend Rows Detected: {len(null_rows)}")
    for nr in null_rows:
        print(f"  - [{nr['period']}] {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
    print("=" * 70)

    return rows, null_rows


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes period-over-period growth strictly for a single ward and category.
    Never aggregates across wards or categories. Shows explicit formulas.
    """
    if not growth_type or not growth_type.strip():
        raise ValueError("Growth type is mandatory and cannot be empty. Please specify --growth-type (e.g., MoM).")

    gt_upper = growth_type.strip().upper()
    if gt_upper != "MOM":
        raise ValueError(f"Unsupported growth-type '{growth_type}'. Only 'MoM' is currently supported.")

    ward_clean = ward.strip()
    category_clean = category.strip()

    # Reject unauthorized cross-ward or cross-category aggregation
    if (
        ward_clean.lower() in DISALLOWED_AGGREGATIONS
        or category_clean.lower() in DISALLOWED_AGGREGATIONS
    ):
        raise ValueError(
            "Unauthorized aggregation request: All-ward or cross-category aggregation is strictly prohibited. "
            "Calculations must be at per-ward and per-category level."
        )

    # Filter strictly to requested ward and category
    filtered = [
        r for r in dataset
        if r["ward"].lower() == ward_clean.lower() and r["category"].lower() == category_clean.lower()
    ]

    if not filtered:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_row = None

    for idx, curr in enumerate(filtered):
        period = curr["period"]
        actual_spend = curr["actual_spend"]
        curr_notes = curr["notes"]

        if idx == 0:
            # Baseline period - no preceding month
            results.append({
                "period": period,
                "ward": curr["ward"],
                "category": curr["category"],
                "actual_spend": actual_spend if actual_spend is not None else "NULL",
                "growth_pct": "NULL",
                "formula": "N/A (Baseline period - no preceding period)",
                "notes": curr_notes,
                "status": "BASELINE",
            })
        else:
            prev_spend = prev_row["actual_spend"]
            prev_period = prev_row["period"]

            if actual_spend is None:
                # Current period has NULL spend
                results.append({
                    "period": period,
                    "ward": curr["ward"],
                    "category": curr["category"],
                    "actual_spend": "NULL",
                    "growth_pct": "NULL",
                    "formula": f"UNCOMPUTABLE (Current actual_spend for {period} is NULL)",
                    "notes": curr_notes or "actual_spend is NULL",
                    "status": "UNCOMPUTABLE",
                })
            elif prev_spend is None:
                # Previous period had NULL spend
                results.append({
                    "period": period,
                    "ward": curr["ward"],
                    "category": curr["category"],
                    "actual_spend": actual_spend,
                    "growth_pct": "NULL",
                    "formula": f"UNCOMPUTABLE (Preceding actual_spend for {prev_period} was NULL)",
                    "notes": f"Preceding period ({prev_period}) missing: {prev_row['notes']}",
                    "status": "UNCOMPUTABLE",
                })
            elif prev_spend == 0:
                results.append({
                    "period": period,
                    "ward": curr["ward"],
                    "category": curr["category"],
                    "actual_spend": actual_spend,
                    "growth_pct": "NULL",
                    "formula": f"UNCOMPUTABLE (Division by zero: preceding spend is 0.0)",
                    "notes": "Preceding period actual_spend was 0.0",
                    "status": "UNCOMPUTABLE",
                })
            else:
                growth_val = ((actual_spend - prev_spend) / prev_spend) * 100.0
                rounded_growth = round(growth_val, 1)
                formula_str = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"

                results.append({
                    "period": period,
                    "ward": curr["ward"],
                    "category": curr["category"],
                    "actual_spend": actual_spend,
                    "growth_pct": f"{rounded_growth:.1f}",
                    "formula": formula_str,
                    "notes": curr_notes,
                    "status": "COMPUTED",
                })

        prev_row = curr

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Exact category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=True, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")

    args = parser.parse_args()

    try:
        dataset, null_audit = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)

        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        fieldnames = [
            "period",
            "ward",
            "category",
            "actual_spend",
            "growth_pct",
            "formula",
            "notes",
            "status",
        ]

        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)

        print(f"\nGrowth computation complete. Wrote {len(results)} rows to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
