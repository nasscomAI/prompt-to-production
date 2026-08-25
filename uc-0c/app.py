"""
UC-0C — Number That Looks Right
Implements agents.md + skills.md enforcement with strict scope, null flagging, and formula transparency.
Run: python app.py --input ../data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
ALLOWED_WARDS = [
    "Ward 1 – Kasba",
    "Ward 2 – Shivajinagar",
    "Ward 3 – Kothrud",
    "Ward 4 – Warje",
    "Ward 5 – Hadapsar",
]
ALLOWED_CATEGORIES = [
    "Roads & Pothole Repair",
    "Drainage & Flooding",
    "Streetlight Maintenance",
    "Waste Management",
    "Parks & Greening",
]
ALLOWED_GROWTH = ["MoM", "YoY"]

# The 5 deliberate null rows for validation
EXPECTED_NULLS = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
}


def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, reports nulls.
    Returns (rows, null_report)
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Input CSV missing columns: {missing}. Found: {reader.fieldnames}")

        rows = []
        null_rows = []
        for i, raw in enumerate(reader, start=2):
            # Normalize
            period = (raw.get("period") or "").strip()
            ward = (raw.get("ward") or "").strip()
            category = (raw.get("category") or "").strip()
            budgeted = (raw.get("budgeted_amount") or "").strip()
            actual_raw = raw.get("actual_spend")
            notes = (raw.get("notes") or "").strip()

            # Parse budgeted
            try:
                budgeted_val = float(budgeted) if budgeted else None
            except ValueError:
                print(f"Warning line {i}: invalid budgeted_amount '{budgeted}'", file=sys.stderr)
                budgeted_val = None

            # Parse actual_spend: blank -> None
            actual_val = None
            actual_str = ""
            if actual_raw is not None:
                actual_str = str(actual_raw).strip()
                if actual_str == "" or actual_str.lower() == "null":
                    actual_val = None
                else:
                    try:
                        actual_val = float(actual_str)
                    except ValueError:
                        print(f"Warning line {i}: invalid actual_spend '{actual_str}'", file=sys.stderr)
                        actual_val = None
            else:
                actual_val = None

            row = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted_val,
                "budgeted_raw": budgeted,
                "actual_spend": actual_val,
                "actual_raw": actual_str,
                "notes": notes,
            }
            rows.append(row)
            if actual_val is None:
                null_rows.append((period, ward, category, notes))

    # Report nulls before returning (enforcement)
    print(f"Loaded {len(rows)} rows from {file_path}")
    print(f"Null actual_spend count: {len(null_rows)}")
    for period, ward, cat, notes in null_rows:
        print(f"  NULL flagged: {period} | {ward} | {cat} | Reason: {notes or 'no notes'}")
    if len(null_rows) != 5:
        print(f"Warning: expected 5 deliberate nulls, found {len(null_rows)}", file=sys.stderr)
    # Validate expected nulls present
    found_set = {(p, w, c) for p, w, c, _ in null_rows}
    missing_expected = EXPECTED_NULLS - found_set
    if missing_expected:
        print(f"Warning: expected null rows missing: {missing_expected}", file=sys.stderr)

    # Sort by period (YYYY-MM lexicographically sorts correctly)
    rows.sort(key=lambda r: r["period"])

    null_report = {"count": len(null_rows), "rows": null_rows}
    return rows, null_report


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Filters to single ward+category, computes MoM or YoY growth with formula.
    """
    # Enforcement: refuse if missing or aggregation requested
    if not ward or ward.strip().lower() in ("all", "*", ""):
        raise ValueError("Refusing to aggregate across wards — please specify a single ward (e.g., 'Ward 1 – Kasba'). No all-ward computation.")
    if not category or category.strip().lower() in ("all", "*", ""):
        raise ValueError("Refusing to aggregate across categories — please specify a single category (e.g., 'Roads & Pothole Repair').")
    if ward not in ALLOWED_WARDS:
        raise ValueError(f"Invalid ward '{ward}'. Allowed: {ALLOWED_WARDS}")
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Allowed: {ALLOWED_CATEGORIES}")
    if not growth_type:
        raise ValueError("Refusing to guess growth type — please specify --growth-type as MoM or YoY explicitly.")
    if growth_type not in ALLOWED_GROWTH:
        raise ValueError(f"Invalid growth-type '{growth_type}'. Allowed: MoM, YoY. Please specify explicitly, no default.")

    # Filter
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'")
    filtered.sort(key=lambda r: r["period"])

    # Build lookup for YoY (same month previous year) — but dataset is only 2024, so YoY will be flagged as no prior year
    period_to_row = {r["period"]: r for r in filtered}

    output = []
    for idx, cur in enumerate(filtered):
        period = cur["period"]
        budgeted = cur["budgeted_raw"]
        actual = cur["actual_spend"]
        actual_raw = cur["actual_raw"]
        notes = cur["notes"]

        # Determine previous value for growth
        prev = None
        if growth_type == "MoM":
            if idx > 0:
                prev = filtered[idx - 1]
        elif growth_type == "YoY":
            # Subtract 1 year from period
            try:
                year, month = period.split("-")
                prev_period = f"{int(year)-1:04d}-{month}"
                prev = period_to_row.get(prev_period)
            except Exception:
                prev = None

        # Flag null rows
        if actual is None:
            growth_percent = ""
            formula = f"NULL — flagged: {notes or 'no reason provided'} — not computed (actual_spend missing for {period})"
            flag_notes = notes
        elif prev is None:
            # First period or no prior year
            growth_percent = ""
            if growth_type == "MoM" and idx == 0:
                formula = f"No prior period — not computed (first period {period}, no previous actual_spend)"
            elif growth_type == "YoY":
                formula = f"No prior year — not computed (no {period} in previous year)"
            else:
                formula = "No prior value — not computed"
            flag_notes = ""
            # If previous actual is null, also flag
            if prev is not None and prev["actual_spend"] is None:
                growth_percent = ""
                formula = f"NULL — flagged: previous period {prev['period']} actual_spend missing ({prev['notes']}) — not computed"
                flag_notes = f"Previous period {prev['period']} flagged: {prev['notes']}"
        elif prev["actual_spend"] is None:
            growth_percent = ""
            formula = f"NULL — flagged: previous period {prev['period']} actual_spend missing ({prev['notes']}) — not computed"
            flag_notes = f"Previous period {prev['period']} flagged: {prev['notes']}"
        else:
            prev_actual = prev["actual_spend"]
            curr_actual = actual
            if prev_actual == 0:
                growth_percent = ""
                formula = f"({curr_actual} - {prev_actual}) / {prev_actual} * 100 = undefined (division by zero) (growth_type={growth_type})"
                flag_notes = ""
            else:
                growth_val = (curr_actual - prev_actual) / prev_actual * 100
                growth_percent = f"{growth_val:+.1f}%"
                # Show formula with values
                formula = f"({curr_actual} - {prev_actual}) / {prev_actual} * 100 = {growth_val:+.1f}% ({growth_type})"
                flag_notes = ""

        out_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_raw if actual is not None else "",
            "growth_percent": growth_percent,
            "formula": formula,
            "flag_notes": flag_notes if actual is None or (prev and prev["actual_spend"] is None) else notes if actual is None else "",
            # Keep original notes in separate column for traceability
            "notes": notes,
        }
        # For non-null rows, flag_notes should be empty or notes if needed
        if actual is not None and prev and prev["actual_spend"] is not None:
            out_row["flag_notes"] = ""
        output.append(out_row)

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth — per-ward per-category, null-flagged, formula-transparent")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help='Single ward, e.g., "Ward 1 – Kasba"')
    parser.add_argument("--category", required=False, default=None, help='Single category, e.g., "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type", help="Growth type: MoM or YoY (required, no default)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: require growth_type explicitly
    if not args.growth_type:
        print("Error: --growth-type is required. Please specify MoM or YoY explicitly. Refusing to guess.", file=sys.stderr)
        sys.exit(1)
    if not args.ward:
        print("Error: --ward is required. Refusing to aggregate across wards. Please specify a single ward.", file=sys.stderr)
        sys.exit(1)
    if not args.category:
        print("Error: --category is required. Refusing to aggregate across categories. Please specify a single category.", file=sys.stderr)
        sys.exit(1)

    try:
        rows, null_report = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"Refused: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_percent", "formula", "flag_notes", "notes"]
    with out_path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for r in output_rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"Done. Computed {args.growth_type} growth for {args.ward} | {args.category}: {len(output_rows)} periods written to {args.output}")
    print(f"Null handling: {null_report['count']} nulls flagged globally; filtered set contains {sum(1 for r in output_rows if not r['actual_spend'])} nulls in scope.")
    # Print verification for reference values
    for r in output_rows:
        if r["period"] in ("2024-07", "2024-10") and args.ward == "Ward 1 – Kasba" and args.category == "Roads & Pothole Repair":
            print(f"  {r['period']}: actual {r['actual_spend']} growth {r['growth_percent']} formula {r['formula']}")


if __name__ == "__main__":
    main()
