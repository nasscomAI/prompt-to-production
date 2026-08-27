"""
UC-0C — Number That Looks Right (Ward Budget Growth Analyzer)
Build guided by agents.md (RICE framework) and skills.md.

Enforcement Rules:
1. Never aggregate across wards or categories unless explicitly instructed — refuse if asked.
2. Flag every null row before computing — report null reason from the notes column.
3. Show formula used in every output row alongside the result.
4. If --growth-type not specified — refuse and ask, never guess.
"""

import argparse
import csv
import os
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


def _normalize_str(s: str) -> str:
    """Normalizes dashes, hyphens, and whitespace for robust string matching."""
    if not s:
        return ""
    # Normalize unicode forms (e.g. en-dash, em-dash, standard hyphen)
    normalized = unicodedata.normalize("NFKD", s)
    normalized = normalized.replace("–", "-").replace("—", "-").replace("−", "-")
    # Collapse consecutive whitespace
    return " ".join(normalized.strip().split()).lower()


def load_dataset(input_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Skill: load_dataset
    Reads an input CSV containing municipal ward budget records, validates required schema,
    and scans for null/missing actual_spend values, reporting total null count and specific
    row details with notes before returning.

    Args:
        input_path: Path to the input CSV file.

    Returns:
        tuple: (dataset_rows, null_records)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: '{input_path}'")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows: List[Dict[str, Any]] = []
    null_records: List[Dict[str, Any]] = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Input CSV '{input_path}' is empty or invalid.")

        header_set = set(reader.fieldnames)
        missing_cols = required_columns - header_set
        if missing_cols:
            raise ValueError(
                f"Input CSV missing required column(s): {', '.join(sorted(missing_cols))}"
            )

        for line_num, row in enumerate(reader, start=2):
            raw_spend = row["actual_spend"].strip() if row["actual_spend"] is not None else ""
            is_null = raw_spend == ""

            parsed_row: Dict[str, Any] = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": float(row["budgeted_amount"].strip()) if row["budgeted_amount"].strip() else 0.0,
                "actual_spend": float(raw_spend) if not is_null else None,
                "notes": row["notes"].strip() if row.get("notes") else "",
                "line_num": line_num,
            }
            rows.append(parsed_row)

            if is_null:
                null_records.append(parsed_row)

    print(f"\n[load_dataset] Loaded {len(rows)} total records from '{input_path}'.")
    print(f"[load_dataset] Scan complete: Found {len(null_records)} row(s) with NULL 'actual_spend':")
    for nr in null_records:
        print(f"  • Line {nr['line_num']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: \"{nr['notes']}\"")
    print()

    return rows, null_records


def compute_growth(
    dataset: List[Dict[str, Any]],
    ward: Optional[str],
    category: Optional[str],
    growth_type: Optional[str],
    null_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth
    Computes period-over-period financial growth rates for a designated ward and category.
    Enforces non-aggregation, transparent formula rendering, and explicit null handling.

    Args:
        dataset: List of dataset records.
        ward: Target ward name.
        category: Target category name.
        growth_type: Growth formula type ('MoM' or 'YoY').
        null_records: List of detected null records.

    Returns:
        List of structured result rows for output.
    """
    # Enforcement Rule 4: Refusal on missing growth formula
    if not growth_type or not growth_type.strip():
        raise ValueError(
            "[REFUSAL] Missing required argument '--growth-type'. "
            "You must explicitly specify a growth type ('MoM' or 'YoY'). "
            "Guessing or silently defaulting formulas is strictly prohibited by enforcement rules."
        )

    norm_growth = growth_type.strip().upper()
    if norm_growth not in ("MOM", "YOY"):
        raise ValueError(
            f"[REFUSAL] Unsupported growth type '{growth_type}'. "
            "Supported growth types are: 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)."
        )

    # Enforcement Rule 1: Never aggregate across wards
    if not ward or not ward.strip():
        raise ValueError(
            "[REFUSAL] Missing required argument '--ward'. "
            "Never aggregate across wards. You must explicitly specify a single ward (e.g., --ward \"Ward 1 – Kasba\")."
        )

    norm_ward_input = _normalize_str(ward)
    if norm_ward_input in ("all", "any", "all wards", "all-ward", "total"):
        raise ValueError(
            f"[REFUSAL] All-ward aggregation requested ('{ward}'). "
            "Aggregating across all wards into a single figure is strictly prohibited by enforcement rules. "
            "Calculations must be performed on a single, specific ward."
        )

    # Enforcement Rule 1: Never aggregate across categories
    if not category or not category.strip():
        raise ValueError(
            "[REFUSAL] Missing required argument '--category'. "
            "Never aggregate across categories. You must explicitly specify a single category (e.g., --category \"Roads & Pothole Repair\")."
        )

    norm_cat_input = _normalize_str(category)
    if norm_cat_input in ("all", "any", "all categories", "total", "combined"):
        raise ValueError(
            f"[REFUSAL] Cross-category aggregation requested ('{category}'). "
            "Aggregating across multiple categories into a single figure is strictly prohibited by enforcement rules. "
            "Calculations must be performed on a single, specific category."
        )

    # Find matching ward and category in dataset
    available_wards = {r["ward"] for r in dataset}
    available_categories = {r["category"] for r in dataset}

    matched_ward = None
    for w in available_wards:
        if _normalize_str(w) == norm_ward_input:
            matched_ward = w
            break

    if not matched_ward:
        raise ValueError(
            f"[ERROR] Ward '{ward}' not found in dataset.\n"
            f"Available wards:\n" + "\n".join(f"  - {w}" for w in sorted(available_wards))
        )

    matched_category = None
    for c in available_categories:
        if _normalize_str(c) == norm_cat_input:
            matched_category = c
            break

    if not matched_category:
        raise ValueError(
            f"[ERROR] Category '{category}' not found in dataset.\n"
            f"Available categories:\n" + "\n".join(f"  - {c}" for c in sorted(available_categories))
        )

    # Filter records for the target ward and category
    filtered = [
        r for r in dataset
        if r["ward"] == matched_ward and r["category"] == matched_category
    ]
    # Sort chronologically by period
    filtered.sort(key=lambda r: r["period"])

    lag_step = 1 if norm_growth == "MOM" else 12
    growth_label = "MoM" if norm_growth == "MOM" else "YoY"

    results: List[Dict[str, Any]] = []

    for i, curr in enumerate(filtered):
        period = curr["period"]
        budgeted = curr["budgeted_amount"]
        curr_spend = curr["actual_spend"]
        curr_notes = curr["notes"]

        # Case 1: Current period actual spend is NULL
        if curr_spend is None:
            reason = curr_notes if curr_notes else "Missing actual spend in dataset"
            results.append({
                "period": period,
                "ward": matched_ward,
                "category": matched_category,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": "NULL",
                "growth_type": growth_label,
                "growth_rate_pct": "NULL",
                "formula_used": f"N/A (Actual spend is NULL — {reason})",
                "flag": "NULL_SPEND_NOT_COMPUTED",
                "notes": curr_notes,
            })
            continue

        # Case 2: Base period (no prior comparison period available)
        if i < lag_step:
            results.append({
                "period": period,
                "ward": matched_ward,
                "category": matched_category,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": f"{curr_spend:.1f}",
                "growth_type": growth_label,
                "growth_rate_pct": "NULL",
                "formula_used": f"N/A (Base period — no prior {growth_label} reference data)",
                "flag": "BASE_PERIOD",
                "notes": curr_notes,
            })
            continue

        prev = filtered[i - lag_step]
        prev_spend = prev["actual_spend"]
        prev_period = prev["period"]
        prev_notes = prev["notes"]

        # Case 3: Prior period actual spend is NULL
        if prev_spend is None:
            reason = prev_notes if prev_notes else f"Missing actual spend in prior period {prev_period}"
            results.append({
                "period": period,
                "ward": matched_ward,
                "category": matched_category,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": f"{curr_spend:.1f}",
                "growth_type": growth_label,
                "growth_rate_pct": "NULL",
                "formula_used": f"N/A (Prior period {prev_period} spend is NULL — {reason})",
                "flag": "PRIOR_PERIOD_NULL_NOT_COMPUTED",
                "notes": curr_notes,
            })
            continue

        # Case 4: Prior spend was 0 (division by zero protection)
        if prev_spend == 0.0:
            results.append({
                "period": period,
                "ward": matched_ward,
                "category": matched_category,
                "budgeted_amount": f"{budgeted:.1f}",
                "actual_spend": f"{curr_spend:.1f}",
                "growth_type": growth_label,
                "growth_rate_pct": "N/A",
                "formula_used": f"N/A (Division by zero — prior period {prev_period} spend is 0.0)",
                "flag": "ZERO_DIVISION_NOT_COMPUTED",
                "notes": curr_notes,
            })
            continue

        # Case 5: Valid computation
        pct = ((curr_spend - prev_spend) / prev_spend) * 100.0
        pct_formatted = f"{pct:+.1f}%"
        formula_str = (
            f"(({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100 = {pct_formatted}"
        )

        results.append({
            "period": period,
            "ward": matched_ward,
            "category": matched_category,
            "budgeted_amount": f"{budgeted:.1f}",
            "actual_spend": f"{curr_spend:.1f}",
            "growth_type": growth_label,
            "growth_rate_pct": pct_formatted,
            "formula_used": formula_str,
            "flag": "COMPUTED",
            "notes": curr_notes,
        })

    return results


def export_results(results: List[Dict[str, Any]], output_path: str) -> None:
    """Exports structured growth results to CSV and prints a clean ASCII preview."""
    if not results:
        print("[export_results] Warning: No rows to export.")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate_pct",
        "formula_used",
        "flag",
        "notes",
    ]

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[export_results] Successfully written {len(results)} rows to '{output_path}'.\n")

    # Display clean tabular preview in console
    print("=" * 115)
    print(f"{'Period':<8} | {'Ward':<22} | {'Category':<24} | {'Spend':<6} | {'Growth':<8} | {'Formula & Details'}")
    print("-" * 115)
    for r in results:
        spend_disp = r['actual_spend']
        growth_disp = r['growth_rate_pct']
        details_disp = r['formula_used']
        if r['notes']:
            details_disp += f" [{r['notes']}]"
        print(f"{r['period']:<8} | {r['ward']:<22} | {r['category']:<24} | {r['actual_spend']:<6} | {growth_disp:<8} | {details_disp}")
    print("=" * 115)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses and returns command-line arguments."""
    parser = argparse.ArgumentParser(
        description="UC-0C — Granular Ward Budget Growth Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        default="../data/budget/ward_budget.csv",
        help="Path to input ward budget CSV file (default: ../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--ward",
        "-w",
        required=False,
        default=None,
        help="Specific ward name (e.g., 'Ward 1 – Kasba'). Aggregation across wards is strictly refused.",
    )
    parser.add_argument(
        "--category",
        "-c",
        required=False,
        default=None,
        help="Specific expenditure category (e.g., 'Roads & Pothole Repair'). Aggregation across categories is strictly refused.",
    )
    parser.add_argument(
        "--growth-type",
        "-g",
        dest="growth_type",
        required=False,
        default=None,
        help="Growth calculation type: 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year). Guessing or defaulting is strictly refused.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="growth_output.csv",
        help="Path to write the resulting growth CSV (default: growth_output.csv)",
    )
    return parser.parse_args(args)


def main():
    args = parse_arguments()

    try:
        # Step 1: Load and scan dataset (load_dataset skill)
        dataset, null_records = load_dataset(args.input)

        # Step 2: Calculate granular growth metrics with strict enforcement (compute_growth skill)
        results = compute_growth(
            dataset=dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
            null_records=null_records,
        )

        # Step 3: Export output CSV and display table
        export_results(results, args.output)

    except ValueError as ve:
        print(f"\n{ve}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as fe:
        print(f"\n[FILE ERROR] {fe}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
