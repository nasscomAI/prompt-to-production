"""
UC-0C -- Number That Looks Right
Built from agents.md (RICE enforcement) and skills.md (skill definitions).

Agent Role:
  Municipal budget growth analysis agent. Computes per-ward per-category
  month-over-month growth. Never aggregates across wards/categories.
  Flags null values explicitly. Shows formula for every computation.

Enforcement Rules:
  1. Never aggregate across wards or categories — refuse if asked.
  2. Flag every null actual_spend row — report reason from notes.
  3. Show formula used in every output row.
  4. If --growth-type not specified — refuse and ask.
  5. Growth % rounded to 1 decimal place.
"""

import argparse
import csv
import sys


# ---------------------------------------------------------------------------
#  Skill: load_dataset
#  Input:  file_path (str)
#  Output: list of row dicts + null report printed
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend"]


def load_dataset(file_path: str) -> list:
    """
    Read the ward budget CSV, validate columns, report nulls.

    Returns list of row dicts. Null actual_spend rows are preserved
    (not removed) with actual_spend set to None.
    """
    # --- Validate input file ---
    try:
        infile = open(file_path, "r", encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot open input file: {e}")
        sys.exit(1)

    try:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            print(f"ERROR: Input file is empty or not a valid CSV: {file_path}")
            sys.exit(1)
    except csv.Error as e:
        print(f"ERROR: Invalid CSV format: {e}")
        sys.exit(1)

    # --- Validate required columns ---
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing_cols:
        print(f"ERROR: Missing required columns: {', '.join(missing_cols)}")
        print(f"  Found columns: {', '.join(reader.fieldnames)}")
        sys.exit(1)

    # --- Read all rows ---
    data = []
    null_rows = []

    for row in reader:
        actual = row.get("actual_spend", "").strip()
        if actual == "":
            row["actual_spend"] = None
            null_rows.append(row)
        else:
            try:
                row["actual_spend"] = float(actual)
            except ValueError:
                row["actual_spend"] = None
                null_rows.append(row)

        try:
            row["budgeted_amount"] = float(row.get("budgeted_amount", 0))
        except (ValueError, TypeError):
            row["budgeted_amount"] = 0.0

        data.append(row)

    infile.close()

    # --- Print null report ---
    print(f"\n--- Data Load Report ---")
    print(f"  Total rows: {len(data)}")
    print(f"  Null actual_spend rows: {len(null_rows)}")

    if null_rows:
        print(f"\n  Null rows detail:")
        for nr in null_rows:
            reason = nr.get("notes", "").strip() or "No reason provided"
            print(f"    - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {reason}")

    print(f"--- End Report ---\n")

    return data


# ---------------------------------------------------------------------------
#  Skill: compute_growth
#  Input:  data (list), ward (str), category (str), growth_type (str)
#  Output: list of dicts — per-period growth table
# ---------------------------------------------------------------------------

SUPPORTED_GROWTH_TYPES = ["MoM"]


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute growth for a specific ward + category + growth_type.

    Enforcement (from agents.md):
      - Filter to exact ward + category — no cross-ward aggregation
      - Flag null rows — do not compute growth for them
      - Show formula in every row
      - First period flagged as FIRST_PERIOD
    """
    # --- Validate growth_type ---
    if not growth_type:
        print("ERROR: --growth-type is required. Supported types: MoM")
        print("  Never guess the growth type — it must be explicitly specified.")
        sys.exit(1)

    if growth_type not in SUPPORTED_GROWTH_TYPES:
        print(f"ERROR: Unsupported growth type: '{growth_type}'")
        print(f"  Supported types: {', '.join(SUPPORTED_GROWTH_TYPES)}")
        sys.exit(1)

    # --- Validate ward exists ---
    available_wards = sorted(set(r["ward"] for r in data))
    if ward not in available_wards:
        print(f"ERROR: Ward '{ward}' not found in dataset.")
        print(f"  Available wards: {', '.join(available_wards)}")
        sys.exit(1)

    # --- Validate category exists ---
    available_categories = sorted(set(r["category"] for r in data))
    if category not in available_categories:
        print(f"ERROR: Category '{category}' not found in dataset.")
        print(f"  Available categories: {', '.join(available_categories)}")
        sys.exit(1)

    # --- Filter data to requested ward + category ---
    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'")
        sys.exit(1)

    # --- Compute MoM growth ---
    results = []
    previous_spend = None

    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        notes = row.get("notes", "").strip()

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "",
            "previous_spend": "",
            "growth_pct": "",
            "formula": "",
            "flag": "",
            "null_reason": "",
        }

        # --- Handle FIRST_PERIOD ---
        if i == 0:
            if actual is None:
                result["actual_spend"] = "NULL"
                result["flag"] = "NULL_VALUE | FIRST_PERIOD"
                result["null_reason"] = notes or "No reason provided"
                result["formula"] = "N/A (null value + first period)"
            else:
                result["actual_spend"] = actual
                result["previous_spend"] = "N/A"
                result["growth_pct"] = "N/A"
                result["formula"] = "N/A (first period — no prior month)"
                result["flag"] = "FIRST_PERIOD"
            previous_spend = actual
            results.append(result)
            continue

        # --- Handle NULL actual_spend ---
        if actual is None:
            result["actual_spend"] = "NULL"
            result["flag"] = "NULL_VALUE"
            result["null_reason"] = notes or "No reason provided"
            result["formula"] = "N/A (null value — cannot compute)"
            previous_spend = None  # Next month also can't compute
            results.append(result)
            continue

        result["actual_spend"] = actual

        # --- Handle NULL previous_spend (prior month was null) ---
        if previous_spend is None:
            result["previous_spend"] = "NULL (prior month)"
            result["growth_pct"] = "N/A"
            result["formula"] = "N/A (prior month was null — cannot compute)"
            result["flag"] = "PRIOR_NULL"
            previous_spend = actual
            results.append(result)
            continue

        # --- Normal MoM computation ---
        result["previous_spend"] = previous_spend

        if previous_spend == 0:
            result["growth_pct"] = "N/A"
            result["formula"] = "N/A (division by zero — prior month spend is 0)"
            result["flag"] = "DIV_BY_ZERO"
        else:
            growth = (actual - previous_spend) / previous_spend * 100
            growth_rounded = round(growth, 1)
            result["growth_pct"] = growth_rounded

            sign = "+" if growth_rounded >= 0 else ""
            result["formula"] = (
                f"({actual} - {previous_spend}) / {previous_spend} * 100 "
                f"= {sign}{growth_rounded}%"
            )

        previous_spend = actual
        results.append(result)

    return results


# ---------------------------------------------------------------------------
#  Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator — Number That Looks Right"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward", required=True,
        help="Ward name (e.g. 'Ward 1 – Kasba')"
    )
    parser.add_argument(
        "--category", required=True,
        help="Category name (e.g. 'Roads & Pothole Repair')"
    )
    parser.add_argument(
        "--growth-type", required=True, dest="growth_type",
        help="Growth type: MoM (required — never guessed)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write growth_output.csv"
    )
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    print(f"Loading data from: {args.input}")
    data = load_dataset(args.input)

    # Step 2: Compute growth
    print(f"Computing {args.growth_type} growth for:")
    print(f"  Ward:     {args.ward}")
    print(f"  Category: {args.category}")
    results = compute_growth(data, args.ward, args.category, args.growth_type)

    # Step 3: Write output CSV
    output_fields = [
        "period", "ward", "category", "actual_spend", "previous_spend",
        "growth_pct", "formula", "flag", "null_reason",
    ]

    try:
        with open(args.output, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}")
        sys.exit(1)

    # Step 4: Summary
    print(f"\n--- Results Summary ---")
    print(f"  Periods processed: {len(results)}")
    null_count = sum(1 for r in results if "NULL_VALUE" in str(r["flag"]))
    if null_count:
        print(f"  Null periods flagged: {null_count}")
        for r in results:
            if "NULL_VALUE" in str(r["flag"]):
                print(f"    - {r['period']}: {r['null_reason']}")

    computed = [r for r in results if r["growth_pct"] not in ("", "N/A")]
    if computed:
        vals = [r["growth_pct"] for r in computed]
        max_growth = max(vals)
        min_growth = min(vals)
        max_period = [r["period"] for r in computed if r["growth_pct"] == max_growth][0]
        min_period = [r["period"] for r in computed if r["growth_pct"] == min_growth][0]
        print(f"  Highest growth: {max_growth}% ({max_period})")
        print(f"  Lowest growth:  {min_growth}% ({min_period})")

    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
