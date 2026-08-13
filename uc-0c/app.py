"""
UC-0C app.py — Budget / Growth Analyzer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from pathlib import Path

FORMULA_MOM = "(actual_spend_t - actual_spend_t_prev) / actual_spend_t_prev * 100"


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """
    Skill: load_dataset
    Reads CSV file using csv.DictReader, validates required columns,
    and identifies all null actual_spend rows along with their notes reasons.
    """
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input budget dataset not found at: {input_path}")

    records = []
    null_records = []
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing_cols = required_cols - fieldnames
        if missing_cols:
            raise ValueError(f"Dataset missing required columns: {missing_cols}")

        for row in reader:
            records.append(row)
            actual = row.get("actual_spend", "").strip()
            if actual == "" or actual.upper() == "NULL":
                null_records.append(row)

    return records, null_records


def compute_growth(records: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Skill: compute_growth
    Filters records for specific ward and category, calculates period-over-period growth (MoM)
    using exact formula, attaches formula strings, and handles null spend flags.
    """
    # Refusal validation
    if not growth_type:
        print("REFUSAL: --growth-type must be explicitly specified (e.g. --growth-type MoM). System will not guess missing parameters.")
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"REFUSAL: Unsupported growth-type '{growth_type}'. Only 'MoM' growth type is supported.")
        sys.exit(1)

    if not ward or ward.strip().lower() in ("all", "all wards", "*"):
        print("REFUSAL: Cross-ward aggregation is not permitted. Please specify a single target ward.")
        sys.exit(1)

    if not category or category.strip().lower() in ("all", "all categories", "*"):
        print("REFUSAL: Cross-category aggregation is not permitted. Please specify a single target category.")
        sys.exit(1)

    # Filter for target ward & category
    filtered = [r for r in records if r["ward"] == ward and r["category"] == category]
    if not filtered:
        print(f"REFUSAL: No records found for ward '{ward}' and category '{category}'.")
        sys.exit(1)

    # Sort chronologically by period
    filtered.sort(key=lambda r: r["period"])

    output_rows = []
    prev_spend = None
    prev_is_null = False

    for row in filtered:
        period = row["period"]
        budgeted = row["budgeted_amount"]
        raw_actual = row.get("actual_spend", "").strip()
        source_note = row.get("notes", "").strip()

        # Check if current spend is null
        if raw_actual == "" or raw_actual.upper() == "NULL":
            curr_spend = None
            is_null = True
        else:
            try:
                curr_spend = float(raw_actual)
                is_null = False
            except ValueError:
                curr_spend = None
                is_null = True

        if is_null:
            growth_pct_str = "NULL"
            actual_display = "NULL"
            note_str = f"NULL: {source_note}" if source_note else "NULL: Value missing"
            prev_spend = None
            prev_is_null = True
        else:
            actual_display = str(curr_spend)
            if prev_spend is None or prev_is_null:
                growth_pct_str = "N/A"
                if prev_is_null:
                    note_str = "N/A: Prior period spend missing (NULL)"
                else:
                    note_str = source_note if source_note else "N/A: First period"
            else:
                growth_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
                sign = "+" if growth_val >= 0 else ""
                growth_pct_str = f"{sign}{growth_val:.1f}%"
                note_str = source_note

            prev_spend = curr_spend
            prev_is_null = False

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_display,
            "growth_type": growth_type,
            "growth_pct": growth_pct_str,
            "formula": FORMULA_MOM,
            "notes": note_str
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget / Growth Analyzer")
    parser.add_argument(
        "--input",
        default="../data/budget/ward_budget.csv",
        help="Path to input budget CSV file"
    )
    parser.add_argument(
        "--ward",
        required=False,
        default=None,
        help="Target ward name (required)"
    )
    parser.add_argument(
        "--category",
        required=False,
        default=None,
        help="Target category name (required)"
    )
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        default=None,
        help="Growth metric type e.g. MoM (required)"
    )
    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Path to output CSV file"
    )

    args = parser.parse_args()

    # Step A: Parameter Refusal Checks
    if not args.growth_type:
        print("REFUSAL: --growth-type must be explicitly specified (e.g. --growth-type MoM). System will not guess missing parameters.")
        sys.exit(1)

    if not args.ward or args.ward.strip().lower() in ("all", "all wards", "*"):
        print("REFUSAL: Cross-ward aggregation is not permitted. Please specify a single target ward.")
        sys.exit(1)

    if not args.category or args.category.strip().lower() in ("all", "all categories", "*"):
        print("REFUSAL: Cross-category aggregation is not permitted. Please specify a single target category.")
        sys.exit(1)

    # Step B: Load dataset
    try:
        records, null_records = load_dataset(args.input)
    except Exception as e:
        print(f"ERROR: Failed to load dataset: {e}")
        sys.exit(1)

    # Step C & D: Compute growth
    output_rows = compute_growth(records, args.ward, args.category, args.growth_type)

    # Step E: Write output to CSV
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_pct",
        "formula",
        "notes"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Successfully generated growth output table at: {args.output}")


if __name__ == "__main__":
    main()
