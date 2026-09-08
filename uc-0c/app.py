"""
UC-0C app.py — Number That Looks Right
Implements load_dataset + compute_growth per skills.md and agents.md enforcement.
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    Returns dict with rows/null_rows or dict with 'error' key.
    """
    p = Path(input_path)

    if p.suffix.lower() != ".csv":
        return {"error": f"invalid input — expected .csv file, got {p.suffix}"}
    if not p.exists():
        return {"error": f"invalid input — file not found: {input_path}"}

    try:
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return {"error": "invalid input — file is empty or missing header"}
            # validate columns
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                return {"error": f"invalid input — missing required columns: {missing}"}

            rows = []
            null_rows = []
            for line_num, raw in enumerate(reader, start=2):
                period = raw.get("period", "").strip()
                ward = raw.get("ward", "").strip()
                category = raw.get("category", "").strip()
                notes = raw.get("notes", "").strip()
                budgeted_raw = raw.get("budgeted_amount", "").strip()
                actual_raw = raw.get("actual_spend", "").strip()

                # budgeted_amount always present but validate
                try:
                    budgeted = float(budgeted_raw) if budgeted_raw != "" else None
                except ValueError:
                    return {"error": f"invalid input — non-numeric budgeted_amount at line {line_num}: {budgeted_raw}"}

                if actual_raw == "" or actual_raw.lower() == "null":
                    actual = None
                    null_rows.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "notes": notes,
                        "line": line_num
                    })
                else:
                    try:
                        actual = float(actual_raw)
                    except ValueError:
                        return {"error": f"invalid input — non-numeric actual_spend at line {line_num}: {actual_raw}"}

                rows.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budgeted,
                    "actual_spend": actual,
                    "notes": notes,
                })

            total_rows = len(rows)
            null_count = len(null_rows)

            if total_rows == 0:
                return {"error": "invalid input — file is empty (no data rows)"}

            # Report null count and which rows before returning (to stderr for visibility, also stdout)
            print(f"[load_dataset] Loaded {total_rows} rows from {input_path}", file=sys.stderr)
            print(f"[load_dataset] Null actual_spend count: {null_count}", file=sys.stderr)
            if null_rows:
                print("[load_dataset] Null rows (must be flagged — not computed):", file=sys.stderr)
                for nr in null_rows:
                    print(f"  - {nr['period']} · {nr['ward']} · {nr['category']} — {nr['notes']}", file=sys.stderr)

            return {
                "rows": rows,
                "columns": reader.fieldnames,
                "null_count": null_count,
                "null_rows": null_rows,
                "total_rows": total_rows,
            }
    except FileNotFoundError:
        return {"error": f"invalid input — file not found: {input_path}"}
    except Exception as e:
        return {"error": f"invalid input — cannot read file: {e}"}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str):
    """
    Takes ward+category+growth_type, returns per-period table with formula shown.
    Returns list[dict] on success or dict with 'error' key on refusal/invalid.
    """
    # Propagate dataset error
    if not dataset or "error" in dataset:
        err = dataset.get("error", "unknown error") if isinstance(dataset, dict) else "invalid dataset"
        return {"error": err}

    # Enforcement: refuse aggregation if ward/category missing/empty/all/any
    def is_all(v):
        if v is None:
            return True
        s = str(v).strip().lower()
        return s == "" or s in ("all", "any", "*")

    if is_all(ward) or is_all(category):
        return {"error": "[REFUSE] Aggregation across wards/categories not allowed — specify a single --ward and --category"}

    if growth_type is None or str(growth_type).strip() == "":
        return {"error": "[REFUSE] --growth-type is required — specify MoM or YoY, will not assume formula"}

    gt = str(growth_type).strip()
    # normalize case-insensitive but preserve canonical
    gt_lower = gt.lower()
    if gt_lower == "mom":
        gt = "MoM"
    elif gt_lower == "yoy":
        gt = "YoY"
    else:
        return {"error": f"[REFUSE] --growth-type is required — specify MoM or YoY, got '{growth_type}'"}

    rows = dataset.get("rows", [])
    # Filter to ward+category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        # Provide helpful error with available values
        wards = sorted(set(r["ward"] for r in rows))
        cats = sorted(set(r["category"] for r in rows))
        return {"error": f"invalid input — ward/category not found: ward='{ward}' category='{category}'. Available wards: {wards}, categories: {cats}"}

    # Sort by period ascending (YYYY-MM lex sort works)
    filtered.sort(key=lambda r: r["period"])

    output = []
    prev_actual = None
    prev_period = None
    prev_notes = ""

    # For YoY we need map period -> actual
    period_map = {r["period"]: r for r in filtered}

    for idx, r in enumerate(filtered):
        period = r["period"]
        actual = r["actual_spend"]
        notes = r["notes"]
        budgeted = r["budgeted_amount"]

        # Determine growth and formula
        if actual is None:
            growth_pct = "NULL"
            formula = f"FLAGGED NULL — {notes}" if notes else "FLAGGED NULL — no data"
            flag = f"Flagged null: {notes}" if notes else "Flagged null"
        else:
            if gt == "MoM":
                if idx == 0:
                    growth_pct = ""
                    formula = "N/A (no prior period)"
                    flag = ""
                elif prev_actual is None:
                    growth_pct = "N/A"
                    formula = f"N/A (prior period {prev_period} flagged NULL: {prev_notes})" if prev_notes else f"N/A (prior period {prev_period} flagged NULL)"
                    flag = f"Prior period {prev_period} was NULL"
                elif prev_actual == 0:
                    growth_pct = "N/A"
                    formula = f"N/A (division by zero, prior 0 at {prev_period})"
                    flag = "Division by zero"
                else:
                    pct = (actual - prev_actual) / prev_actual * 100
                    # Keep full float for output, also format to 1 decimal for verification logs
                    growth_pct = round(pct, 1)
                    # Show exact values as stored (one decimal in source)
                    # Use minimal formatting: remove trailing zeros if needed but keep 1 decimal for consistency
                    prev_str = str(prev_actual).rstrip("0").rstrip(".") if "." in str(prev_actual) else str(prev_actual)
                    curr_str = str(actual).rstrip("0").rstrip(".") if "." in str(actual) else str(actual)
                    # Ensure at least one decimal shown as in dataset (e.g., 14.8)
                    # Better to format to preserve source precision: we keep original float repr but ensure one decimal if integer
                    # Use original float values directly for formula readability
                    formula = f"({actual}-{prev_actual})/{prev_actual}"
                    flag = ""
            else:  # YoY
                # Need same month previous year: subtract 1 from year
                try:
                    year, month = period.split("-")
                    prev_year_period = f"{int(year)-1:04d}-{month}"
                except ValueError:
                    prev_year_period = None
                yoy_row = period_map.get(prev_year_period) if prev_year_period else None
                if yoy_row is None:
                    growth_pct = "N/A"
                    formula = f"N/A (no YoY prior period {prev_year_period})"
                    flag = "No YoY prior year data (dataset is 2024 only)"
                elif yoy_row["actual_spend"] is None:
                    growth_pct = "N/A"
                    formula = f"N/A (YoY prior {prev_year_period} flagged NULL: {yoy_row['notes']})"
                    flag = f"YoY prior {prev_year_period} was NULL"
                elif yoy_row["actual_spend"] == 0:
                    growth_pct = "N/A"
                    formula = f"N/A (division by zero, YoY prior 0 at {prev_year_period})"
                    flag = "Division by zero"
                else:
                    prev_yoy = yoy_row["actual_spend"]
                    pct = (actual - prev_yoy) / prev_yoy * 100
                    growth_pct = round(pct, 1)
                    formula = f"({actual}-{prev_yoy})/{prev_yoy}"
                    flag = ""

        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "growth_pct": growth_pct,
            "formula": formula,
            "notes": notes,
            "flag": flag,
            "growth_type": gt,
        })

        prev_actual = actual
        prev_period = period
        prev_notes = notes

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth — per-ward per-category with null flagging and formula transparency")
    parser.add_argument("--input", required=True, help="Path to input ward budget CSV")
    parser.add_argument("--ward", required=False, default=None, help="Single ward name (e.g. 'Ward 1 – Kasba') — aggregation refused if missing")
    parser.add_argument("--category", required=False, default=None, help="Single category name (e.g. 'Roads & Pothole Repair') — aggregation refused if missing")
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type", help="Growth type: MoM or YoY — required, will not assume")
    parser.add_argument("--output", required=True, help="Path to output growth CSV")
    args = parser.parse_args()

    # Agents enforcement: refuse if growth_type missing, refuse aggregation if ward/category missing
    if args.growth_type is None or str(args.growth_type).strip() == "":
        print("[REFUSE] --growth-type is required — specify MoM or YoY, will not assume formula", file=sys.stderr)
        print("Usage: python app.py --input <csv> --ward \"<ward>\" --category \"<category>\" --growth-type MoM --output <out.csv>", file=sys.stderr)
        sys.exit(2)

    if args.ward is None or str(args.ward).strip() in ("", "all", "any", "*") or args.category is None or str(args.category).strip() in ("", "all", "any", "*"):
        print("[REFUSE] Aggregation across wards/categories not allowed — specify a single --ward and --category", file=sys.stderr)
        print(f"Received --ward='{args.ward}' --category='{args.category}' — must specify one ward and one category", file=sys.stderr)
        sys.exit(2)

    dataset = load_dataset(args.input)
    if "error" in dataset:
        print(f"Error loading dataset: {dataset['error']}", file=sys.stderr)
        sys.exit(1)

    result = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if isinstance(result, dict) and "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        # Distinguish refusal (exit 2) vs invalid input (exit 1)
        exit_code = 2 if "[REFUSE]" in result["error"] else 1
        sys.exit(exit_code)

    # Write output CSV — every row must have formula
    out_path = Path(args.output)
    if str(out_path.parent) not in (".", ""):
        out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "notes", "flag"]
    # Also include growth_type as column for transparency? Add but keep fieldnames stable; we add growth_type info in header via comment? Better keep columns as above.
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in result:
            # Prepare row: actual_spend None -> empty string for CSV but notes/flag preserve
            row_out = {
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "budgeted_amount": r["budgeted_amount"],
                "actual_spend": "" if r["actual_spend"] is None else r["actual_spend"],
                "growth_pct": r["growth_pct"],
                "formula": r["formula"],
                "notes": r["notes"],
                "flag": r["flag"],
            }
            writer.writerow(row_out)

    print(f"Growth table written to {out_path} ({len(result)} periods, growth_type={args.growth_type}, ward={args.ward}, category={args.category})", file=sys.stderr)
    # Also verify reference values if this is the canonical case
    if args.ward == "Ward 1 – Kasba" and args.category == "Roads & Pothole Repair" and args.growth_type.lower() == "mom":
        # quick sanity check
        lookup = {r["period"]: r for r in result}
        for check_period, expected_pct in [("2024-07", 33.1), ("2024-10", -34.8)]:
            got = lookup.get(check_period, {}).get("growth_pct")
            if got != expected_pct:
                print(f"[WARN] Reference check failed for {check_period}: expected {expected_pct} got {got}", file=sys.stderr)
            else:
                print(f"[OK] Verified {check_period}: growth {got}% matches reference", file=sys.stderr)


if __name__ == "__main__":
    main()
