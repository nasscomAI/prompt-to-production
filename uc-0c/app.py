"""
UC-0C — Ward Budget Growth Calculator (Number That Looks Right)
Municipal budget analytics CLI computing per-ward, per-category growth rates with explicit null flagging.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes"
]

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth",
    "formula_used",
    "flag"
]


def normalize_dash(text: str) -> str:
    """Normalize dashes/hyphens and strip excess whitespace for robust comparison."""
    if not text:
        return ""
    # Normalize en-dash, em-dash, minus sign to standard hyphen
    return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-").strip()


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Skill: load_dataset
    Reads the CSV, validates required columns, and detects all null actual_spend rows.
    Returns: (all_rows, null_rows)
    """
    if not os.path.exists(input_path):
        sys.stderr.write(f"Error: Input file not found: '{input_path}'\n")
        sys.exit(1)

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                sys.stderr.write(f"Error: Input file '{input_path}' is empty or not a valid CSV.\n")
                sys.exit(1)

            actual_fields = [f.strip() for f in reader.fieldnames if f]
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in actual_fields]
            if missing_cols:
                sys.stderr.write(
                    f"Error: Input CSV is missing required column(s): {', '.join(missing_cols)}\n"
                    f"Expected columns: {', '.join(REQUIRED_COLUMNS)}\n"
                    f"Found columns: {', '.join(actual_fields)}\n"
                )
                sys.exit(1)

            all_rows = list(reader)

    except Exception as e:
        sys.stderr.write(f"Error reading input CSV '{input_path}': {e}\n")
        sys.exit(1)

    # Scan for null / blank actual_spend rows
    null_rows = []
    for r in all_rows:
        val = r.get("actual_spend")
        if val is None or val.strip() == "":
            null_rows.append(r)

    # Report null rows to stderr before any computation
    sys.stderr.write(f"Audit: Found {len(null_rows)} rows with null/blank actual_spend across dataset ({len(all_rows)} total rows):\n")
    for r in null_rows:
        p = r.get("period", "UNKNOWN")
        w = r.get("ward", "UNKNOWN")
        c = r.get("category", "UNKNOWN")
        n = r.get("notes", "No reason provided")
        sys.stderr.write(f"  - [{p}] Ward: '{w}' | Category: '{c}' | Reason: '{n}'\n")

    return all_rows, null_rows


def compute_growth(
    dataset: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str
) -> List[Dict[str, str]]:
    """
    Skill: compute_growth
    Computes per-period growth (MoM or YoY) for exactly one ward and category.
    Flags any period whose actual_spend or reference actual_spend is null.
    """
    norm_target_ward = normalize_dash(ward).lower()
    norm_target_cat = normalize_dash(category).lower()

    # Filter strictly by ward and category
    filtered_rows = [
        r for r in dataset
        if normalize_dash(r.get("ward", "")).lower() == norm_target_ward
        and normalize_dash(r.get("category", "")).lower() == norm_target_cat
    ]

    if not filtered_rows:
        sys.stderr.write(
            f"Error: Refusal — No rows found matching Ward: '{ward}' and Category: '{category}'.\n"
            f"The system strictly operates per-ward and per-category and refuses to aggregate or substitute data.\n"
        )
        sys.exit(1)

    # Sort filtered rows chronologically by period
    filtered_rows.sort(key=lambda x: x.get("period", ""))

    output_rows = []

    if growth_type == "MoM":
        for i, row in enumerate(filtered_rows):
            period = row.get("period", "")
            row_ward = row.get("ward", "")
            row_cat = row.get("category", "")
            act_str = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()

            out_row = {
                "period": period,
                "ward": row_ward,
                "category": row_cat,
                "actual_spend": act_str if act_str else "NULL",
                "growth": "",
                "formula_used": "",
                "flag": ""
            }

            if i == 0:
                # Base period
                if not act_str:
                    out_row["growth"] = "NULL_FLAGGED"
                    out_row["formula_used"] = f"Base period has null actual_spend ({notes})"
                    out_row["flag"] = "NULL_ACTUAL_SPEND"
                else:
                    out_row["growth"] = "N/A"
                    out_row["formula_used"] = "Base period (no prior month available)"
                    out_row["flag"] = ""
            else:
                prev_row = filtered_rows[i - 1]
                prev_period = prev_row.get("period", "")
                prev_act_str = prev_row.get("actual_spend", "").strip()
                prev_notes = prev_row.get("notes", "").strip()

                if not act_str:
                    out_row["growth"] = "NULL_FLAGGED"
                    out_row["formula_used"] = f"Cannot compute MoM: actual_spend for current period ({period}) is null ({notes})"
                    out_row["flag"] = "NULL_ACTUAL_SPEND"
                elif not prev_act_str:
                    out_row["growth"] = "NULL_FLAGGED"
                    out_row["formula_used"] = f"Cannot compute MoM: actual_spend for prior period ({prev_period}) is null ({prev_notes})"
                    out_row["flag"] = "NULL_PRIOR_PERIOD"
                else:
                    try:
                        curr_val = float(act_str)
                        prev_val = float(prev_act_str)
                        growth_pct = ((curr_val - prev_val) / prev_val) * 100.0
                        out_row["growth"] = f"{growth_pct:+.1f}%"
                        out_row["formula_used"] = f"MoM = ({curr_val} - {prev_val}) / {prev_val} = {growth_pct:+.1f}%"
                        out_row["flag"] = ""
                    except ValueError as e:
                        out_row["growth"] = "ERROR"
                        out_row["formula_used"] = f"Calculation error parsing numbers: {e}"
                        out_row["flag"] = "INVALID_NUMBER"

            output_rows.append(out_row)

    elif growth_type == "YoY":
        # Build period lookup map for the target ward and category
        period_map = {r.get("period", ""): r for r in filtered_rows}

        for row in filtered_rows:
            period = row.get("period", "")
            row_ward = row.get("ward", "")
            row_cat = row.get("category", "")
            act_str = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()

            out_row = {
                "period": period,
                "ward": row_ward,
                "category": row_cat,
                "actual_spend": act_str if act_str else "NULL",
                "growth": "",
                "formula_used": "",
                "flag": ""
            }

            # Attempt to locate prior year period (YYYY - 1)
            parts = period.split("-")
            if len(parts) == 2 and parts[0].isdigit():
                prior_year = int(parts[0]) - 1
                prior_period = f"{prior_year:04d}-{parts[1]}"
            else:
                prior_period = ""

            if prior_period in period_map:
                prev_row = period_map[prior_period]
                prev_act_str = prev_row.get("actual_spend", "").strip()
                prev_notes = prev_row.get("notes", "").strip()

                if not act_str:
                    out_row["growth"] = "NULL_FLAGGED"
                    out_row["formula_used"] = f"Cannot compute YoY: actual_spend for current period ({period}) is null ({notes})"
                    out_row["flag"] = "NULL_ACTUAL_SPEND"
                elif not prev_act_str:
                    out_row["growth"] = "NULL_FLAGGED"
                    out_row["formula_used"] = f"Cannot compute YoY: actual_spend for prior year period ({prior_period}) is null ({prev_notes})"
                    out_row["flag"] = "NULL_PRIOR_PERIOD"
                else:
                    try:
                        curr_val = float(act_str)
                        prev_val = float(prev_act_str)
                        growth_pct = ((curr_val - prev_val) / prev_val) * 100.0
                        out_row["growth"] = f"{growth_pct:+.1f}%"
                        out_row["formula_used"] = f"YoY = ({curr_val} - {prev_val}) / {prev_val} = {growth_pct:+.1f}%"
                        out_row["flag"] = ""
                    except ValueError as e:
                        out_row["growth"] = "ERROR"
                        out_row["formula_used"] = f"Calculation error parsing numbers: {e}"
                        out_row["flag"] = "INVALID_NUMBER"
            else:
                out_row["growth"] = "INSUFFICIENT_DATA"
                out_row["formula_used"] = f"Cannot compute YoY: no prior year data for period ({period}) in dataset"
                out_row["flag"] = "NO_PRIOR_YEAR_DATA"

            output_rows.append(out_row)

    return output_rows


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Municipal Ward Budget Growth Analytics",
        add_help=True
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific budget category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, default=None,
                        help="Growth calculation type: strictly 'MoM' or 'YoY'")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")

    args = parser.parse_args()

    # Rule 4 & Skill validation: If --growth-type is missing or invalid, refuse and exit
    if not args.growth_type or args.growth_type not in ["MoM", "YoY"]:
        sys.stderr.write(
            "Error: Refusal — --growth-type must be explicitly specified as either 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year).\n"
            "The system refuses to guess or silently default to a growth type.\n"
        )
        sys.exit(1)

    # 1. Load dataset & scan nulls
    all_rows, _ = load_dataset(args.input)

    # 2. Compute growth
    result_table = compute_growth(
        dataset=all_rows,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )

    # 3. Write output CSV
    try:
        with open(args.output, mode="w", encoding="utf-8-sig", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(result_table)
        print(f"Success: Computed {len(result_table)} period rows for '{args.ward}' / '{args.category}' ({args.growth_type}) -> '{args.output}'")
    except Exception as e:
        sys.stderr.write(f"Error writing output CSV '{args.output}': {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
