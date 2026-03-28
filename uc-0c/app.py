"""
UC-0C — Infrastructure Budget Growth Calculator
Built using RICE → agents.md → skills.md → CRAFT workflow.

Failure modes guarded against:
- Wrong aggregation level  : only one ward + one category at a time
- Silent null handling     : all nulls flagged before computation
- Formula assumption       : growth_type must be specified, never guessed
"""
import argparse
import csv
import sys
from typing import Optional


# ── Skill 1: load_dataset ────────────────────────────────────────────────────

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, report nulls before returning.

    Returns:
        dict with keys:
          - 'rows'  : list of all row dicts
          - 'nulls' : list of null actual_spend row dicts (with notes)
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = set(col.strip().lower() for col in (reader.fieldnames or []))

            missing = required_columns - headers
            if missing:
                print(f"ERROR: Missing required columns: {missing}")
                print(f"  Found columns: {reader.fieldnames}")
                sys.exit(1)

            rows = []
            for row in reader:
                # Normalise keys to lowercase stripped
                clean = {k.strip().lower(): v.strip() for k, v in row.items()}
                rows.append(clean)

    except FileNotFoundError:
        print(f"ERROR: Input file not found: '{file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}")
        sys.exit(1)

    if not rows:
        print("ERROR: CSV file contains no data rows.")
        sys.exit(1)

    # ── Flag nulls BEFORE returning ──────────────────────────────────────
    null_rows = []
    for row in rows:
        if not row.get("actual_spend"):
            null_rows.append({
                "period":   row.get("period", ""),
                "ward":     row.get("ward", ""),
                "category": row.get("category", ""),
                "notes":    row.get("notes", "No reason provided"),
            })

    print(f"  Dataset loaded : {len(rows)} rows total")
    print(f"  Null rows found: {len(null_rows)}")
    if null_rows:
        print("  ── Null actual_spend rows (flagged before computation) ──")
        for n in null_rows:
            print(f"     {n['period']} | {n['ward']} | {n['category']} | Reason: {n['notes']}")
        print()

    return {"rows": rows, "nulls": null_rows}


# ── Skill 2: compute_growth ──────────────────────────────────────────────────

def compute_growth(
    dataset: dict,
    ward: str,
    category: str,
    growth_type: str,
    output_path: str,
) -> None:
    """
    Compute per-period growth for one ward + one category.

    Enforcement:
    - Refuses if growth_type not MoM or YoY
    - Refuses if ward or category not found
    - Marks null rows as NULL_FLAGGED, skips formula
    - Never aggregates — always per-period table
    - Shows exact formula in every non-null row
    """

    # ── Validate growth_type ─────────────────────────────────────────────
    if growth_type not in ("MoM", "YoY"):
        print(f"ERROR: --growth-type must be 'MoM' or 'YoY'. Got: '{growth_type}'")
        print("  Refusing to guess the formula. Please specify one of: MoM, YoY")
        sys.exit(1)

    rows = dataset["rows"]

    # ── Filter to requested ward + category ──────────────────────────────
    filtered = [
        r for r in rows
        if r.get("ward", "").strip() == ward.strip()
        and r.get("category", "").strip() == category.strip()
    ]

    if not filtered:
        # Check if ward exists at all
        all_wards      = sorted(set(r.get("ward", "") for r in rows))
        all_categories = sorted(set(r.get("category", "") for r in rows))
        print(f"ERROR: No data found for ward='{ward}' and category='{category}'")
        print(f"  Available wards      : {all_wards}")
        print(f"  Available categories : {all_categories}")
        sys.exit(1)

    # ── Sort by period ───────────────────────────────────────────────────
    filtered.sort(key=lambda r: r.get("period", ""))

    # ── Determine formula label ──────────────────────────────────────────
    if growth_type == "MoM":
        formula_label = "MoM Growth = (current - previous) / previous × 100"
        lookback = 1   # 1 period back
    else:  # YoY
        formula_label = "YoY Growth = (current - same_month_prev_year) / same_month_prev_year × 100"
        lookback = 12  # 12 periods back

    print(f"  Computing {growth_type} growth for: {ward} | {category}")
    print(f"  Formula: {formula_label}")
    print(f"  Periods : {len(filtered)}")
    print()

    # ── Build output rows ────────────────────────────────────────────────
    output_rows = []

    for i, row in enumerate(filtered):
        period       = row.get("period", "")
        actual_raw   = row.get("actual_spend", "").strip()
        is_null      = not actual_raw

        if is_null:
            output_rows.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  "NULL",
                "growth_value":  "NULL_FLAGGED",
                "formula":       "Skipped — actual_spend is null",
                "flag":          "NULL_FLAGGED",
            })
            continue

        actual = float(actual_raw)

        # ── Look up comparison period ────────────────────────────────
        if i < lookback:
            # Not enough history
            output_rows.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  f"{actual:.2f}",
                "growth_value":  "N/A",
                "formula":       f"No prior period available for {growth_type} computation",
                "flag":          "",
            })
            continue

        prior_row     = filtered[i - lookback]
        prior_raw     = prior_row.get("actual_spend", "").strip()
        prior_period  = prior_row.get("period", "")
        prior_is_null = not prior_raw

        if prior_is_null:
            output_rows.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  f"{actual:.2f}",
                "growth_value":  "N/A",
                "formula":       f"Prior period {prior_period} is null — growth cannot be computed",
                "flag":          "PRIOR_NULL",
            })
            continue

        prior = float(prior_raw)

        if prior == 0:
            output_rows.append({
                "period":        period,
                "ward":          ward,
                "category":      category,
                "actual_spend":  f"{actual:.2f}",
                "growth_value":  "N/A",
                "formula":       f"Prior period {prior_period} spend = 0 — division by zero avoided",
                "flag":          "PRIOR_ZERO",
            })
            continue

        growth = ((actual - prior) / prior) * 100
        sign   = "+" if growth >= 0 else ""

        output_rows.append({
            "period":        period,
            "ward":          ward,
            "category":      category,
            "actual_spend":  f"{actual:.2f}",
            "growth_value":  f"{sign}{growth:.1f}%",
            "formula":       f"({actual:.2f} - {prior:.2f}) / {prior:.2f} × 100 = {sign}{growth:.1f}%",
            "flag":          "",
        })

    # ── Write output CSV ─────────────────────────────────────────────────
    output_fields = ["period", "ward", "category", "actual_spend", "growth_value", "formula", "flag"]

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(output_rows)
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}")
        sys.exit(1)

    null_count = sum(1 for r in output_rows if r["flag"] == "NULL_FLAGGED")
    print(f"  Output rows    : {len(output_rows)}")
    print(f"  Nulls flagged  : {null_count}")
    print(f"  Output written : {output_path}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name to compute growth for")
    parser.add_argument("--category",    required=True,  help="Category to compute growth for")
    parser.add_argument("--growth-type", required=True,  help="Growth type: MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    print(f"Running UC-0C Budget Growth Calculator")
    print(f"  Input       : {args.input}")
    print(f"  Ward        : {args.ward}")
    print(f"  Category    : {args.category}")
    print(f"  Growth type : {args.growth_type}")
    print(f"  Output      : {args.output}")
    print()

    # Skill 1 — load and flag nulls
    dataset = load_dataset(args.input)

    # Skill 2 — compute growth
    compute_growth(
        dataset     = dataset,
        ward        = args.ward,
        category    = args.category,
        growth_type = args.growth_type,
        output_path = args.output,
    )

    print("Done.")