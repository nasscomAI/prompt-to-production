"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth per agents.md and skills.md.

Enforcement (from agents.md):
  - Never aggregate across wards or categories
  - Flag every null actual_spend row before computing — report null reason
  - Show formula used in every output row alongside the result
  - If --growth-type not specified, refuse and ask
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(file_path: str) -> dict:
    """
    Reads the ward budget CSV, validates all expected columns, and reports nulls.

    Returns:
        {
            "rows": [list of row dicts with actual_spend as float or None],
            "null_report": [{"row_index": int, "ward": str, "category": str,
                             "period": str, "notes": str}, ...],
            "ward_names": set of unique ward names,
            "category_names": set of unique category names,
        }

    Enforcement (from skills.md):
      - If required columns missing, halt and report which ones
      - Do not proceed with partial schema
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print(f"ERROR: {file_path} is empty or has no header.", file=sys.stderr)
                sys.exit(1)

            # Validate required columns
            missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                print(
                    f"ERROR: {file_path} is missing required columns: {missing}. "
                    f"Found columns: {reader.fieldnames}",
                    file=sys.stderr,
                )
                sys.exit(1)

            raw_rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not raw_rows:
        print(f"ERROR: {file_path} contains no data rows.", file=sys.stderr)
        sys.exit(1)

    # Parse rows — convert actual_spend to float or None
    rows = []
    null_report = []
    ward_names = set()
    category_names = set()

    for i, raw in enumerate(raw_rows):
        row = {
            "period": raw["period"].strip(),
            "ward": raw["ward"].strip(),
            "category": raw["category"].strip(),
            "budgeted_amount": float(raw["budgeted_amount"].strip()),
            "actual_spend": None,
            "notes": raw["notes"].strip() if raw["notes"] else "",
        }

        ward_names.add(row["ward"])
        category_names.add(row["category"])

        actual_raw = raw["actual_spend"].strip()
        if actual_raw:
            row["actual_spend"] = float(actual_raw)
        else:
            # Null row — report it
            null_report.append({
                "row_index": i + 2,  # +2 for 1-indexed header
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "notes": row["notes"],
            })

        rows.append(row)

    return {
        "rows": rows,
        "null_report": null_report,
        "ward_names": ward_names,
        "category_names": category_names,
    }


def _validate_growth_type(growth_type: str) -> str:
    """
    Validate that growth_type is MoM or YoY.

    Enforcement (from agents.md + skills.md):
      - If not MoM or YoY, refuse and ask
    """
    valid = {"MoM", "YoY"}
    if growth_type not in valid:
        print(
            f"ERROR: growth_type must be one of {valid}. Got: '{growth_type}'. "
            f"Please specify --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)
    return growth_type


def compute_growth(ward: str, category: str, growth_type: str, dataset: dict) -> list[dict]:
    """
    Takes ward, category, and growth_type, computes period-by-period growth.

    Returns:
        List of dicts: [{"period": str, "actual_spend": float|None,
                         "growth_value": str|None, "formula_used": str|None,
                         "is_null_flag": bool, "null_reason": str}, ...]

    Enforcement (from agents.md):
      - Flag every null row before computing — report null reason from notes
      - Show formula used in every output row alongside the result
      - Never aggregate across wards or categories

    Enforcement (from skills.md):
      - If ward or category not found, report and do not return empty results silently
    """
    growth_type = _validate_growth_type(growth_type)

    # Validate ward exists
    if ward not in dataset["ward_names"]:
        print(
            f"ERROR: Ward '{ward}' not found in dataset. "
            f"Available wards: {sorted(dataset['ward_names'])}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate category exists
    if category not in dataset["category_names"]:
        print(
            f"ERROR: Category '{category}' not found in dataset. "
            f"Available categories: {sorted(dataset['category_names'])}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Filter to requested ward + category, sorted by period
    filtered = [
        r for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(
            f"ERROR: No data found for ward='{ward}', category='{category}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    results = []

    for idx, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]

        # Check if current row is null
        if actual is None:
            results.append({
                "period": period,
                "actual_spend": None,
                "growth_value": None,
                "formula_used": None,
                "is_null_flag": True,
                "null_reason": row["notes"] or "No reason provided",
            })
            continue

        # Find previous period for growth calculation
        prev_row = None
        if growth_type == "MoM" and idx > 0:
            prev_row = filtered[idx - 1]
        elif growth_type == "YoY":
            # Find same month in previous year (period format: YYYY-MM)
            try:
                year, month = period.split("-")
                prev_year = str(int(year) - 1)
                prev_period = f"{prev_year}-{month}"
                prev_row = next(
                    (r for r in filtered if r["period"] == prev_period), None
                )
            except (ValueError, IndexError):
                prev_row = None

        # Compute growth
        if prev_row is None or prev_row["actual_spend"] is None:
            # No previous data to compare
            if idx == 0 and growth_type == "MoM":
                formula = f"({actual:.1f} − N/A) / N/A × 100 = N/A (no prior period)"
                results.append({
                    "period": period,
                    "actual_spend": actual,
                    "growth_value": "N/A",
                    "formula_used": formula,
                    "is_null_flag": False,
                    "null_reason": "",
                })
            elif prev_row and prev_row["actual_spend"] is None:
                formula = (
                    f"({actual:.1f} − NULL) / |NULL| × 100 = FLAGGED "
                    f"(prior period {prev_row['period']} is null: {prev_row['notes']})"
                )
                results.append({
                    "period": period,
                    "actual_spend": actual,
                    "growth_value": "FLAGGED",
                    "formula_used": formula,
                    "is_null_flag": True,
                    "null_reason": f"Prior period {prev_row['period']} is null: {prev_row['notes']}",
                })
            else:
                formula = f"({actual:.1f} − N/A) / N/A × 100 = N/A (no prior {growth_type} period)"
                results.append({
                    "period": period,
                    "actual_spend": actual,
                    "growth_value": "N/A",
                    "formula_used": formula,
                    "is_null_flag": False,
                    "null_reason": "",
                })
            continue

        prev_actual = prev_row["actual_spend"]
        growth = ((actual - prev_actual) / abs(prev_actual)) * 100
        sign = "+" if growth >= 0 else ""
        formula = f"({actual:.1f} − {prev_actual:.1f}) / |{prev_actual:.1f}| × 100 = {sign}{growth:.1f}%"

        results.append({
            "period": period,
            "actual_spend": actual,
            "growth_value": f"{sign}{growth:.1f}%",
            "formula_used": formula,
            "is_null_flag": False,
            "null_reason": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget growth analysis (per-ward, per-category)"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    dataset = load_dataset(args.input)
    null_count = len(dataset["null_report"])

    print(f"Loaded {len(dataset['rows'])} rows from {args.input}")
    print(f"Wards: {sorted(dataset['ward_names'])}")
    print(f"Categories: {sorted(dataset['category_names'])}")
    print(f"Null actual_spend rows: {null_count}")

    # Enforcement: flag every null row before computing
    if null_count > 0:
        print("\n--- NULL REPORT ---")
        for nr in dataset["null_report"]:
            print(
                f"  Row {nr['row_index']}: {nr['period']} | {nr['ward']} | "
                f"{nr['category']} | Reason: {nr['notes']}"
            )
        print("-------------------\n")

    # Step 2: Compute growth
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)

    # Step 3: Write output CSV
    fieldnames = ["period", "actual_spend", "growth_value", "formula_used", "null_flag", "null_reason"]
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "period": r["period"],
                    "actual_spend": f"{r['actual_spend']:.1f}" if r["actual_spend"] is not None else "NULL",
                    "growth_value": r["growth_value"],
                    "formula_used": r["formula_used"],
                    "null_flag": "YES" if r["is_null_flag"] else "",
                    "null_reason": r["null_reason"],
                })
    except Exception as e:
        print(f"ERROR: Could not write to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

    # Summary
    flagged = sum(1 for r in results if r["is_null_flag"])
    computed = sum(1 for r in results if r["growth_value"] not in (None, "N/A", "FLAGGED"))
    print(f"\nWard: {args.ward}")
    print(f"Category: {args.category}")
    print(f"Growth type: {args.growth_type}")
    print(f"Periods computed: {computed} | Flagged/null: {flagged}")
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
