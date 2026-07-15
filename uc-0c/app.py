"""
UC-0C — Number That Looks Right
Budget Growth Calculator implementing the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ── Skill 1: load_dataset ──────────────────────────────────────────────────────

def load_dataset(input_path: str):
    """
    Read the ward_budget CSV, validate columns, identify null actual_spend rows,
    and return (all_rows, null_rows) before any computation begins.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
                missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
                sys.exit(f"ERROR: CSV is missing required columns: {missing}")

            all_rows = []
            null_rows = []

            for row in reader:
                all_rows.append(row)
                if row["actual_spend"].strip() == "":
                    null_rows.append({
                        "period":   row["period"],
                        "ward":     row["ward"],
                        "category": row["category"],
                        "reason":   row["notes"].strip() if row["notes"].strip() else "No reason provided"
                    })

            if not all_rows:
                sys.exit("ERROR: The CSV file is empty.")

    except FileNotFoundError:
        sys.exit(f"ERROR: File not found — {input_path}")

    return all_rows, null_rows


# ── Skill 2: compute_growth ────────────────────────────────────────────────────

def compute_growth(all_rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    For a given ward, category, and growth_type (MoM or YoY), compute per-period
    spend growth. Every output row includes the formula used.
    Null rows are flagged and NOT interpolated.
    """
    if growth_type not in ("MoM", "YoY"):
        sys.exit(
            "ERROR: --growth-type must be either 'MoM' or 'YoY'. "
            "Please specify which growth calculation you need."
        )

    # Filter rows for this ward + category
    filtered = [
        r for r in all_rows
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        valid_wards = sorted(set(r["ward"] for r in all_rows))
        valid_cats  = sorted(set(r["category"] for r in all_rows))
        sys.exit(
            f"ERROR: No data found for ward='{ward}', category='{category}'.\n"
            f"Valid wards: {valid_wards}\n"
            f"Valid categories: {valid_cats}"
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    if growth_type == "MoM":
        formula_template = "MoM Growth = (current - previous) / previous × 100%"
        lookback = 1
    else:  # YoY
        formula_template = "YoY Growth = (current - prior_year) / prior_year × 100%"
        lookback = 12

    output_rows = []
    for i, row in enumerate(filtered):
        period       = row["period"]
        spend_raw    = row["actual_spend"].strip()
        null_flag    = spend_raw == ""
        null_reason  = (row["notes"].strip() if row["notes"].strip() else "No reason provided") if null_flag else ""

        if null_flag:
            output_rows.append({
                "period":       period,
                "actual_spend": "NULL",
                "growth_pct":   "N/A",
                "formula":      formula_template,
                "null_flag":    "TRUE",
                "null_reason":  null_reason,
            })
            continue

        spend = float(spend_raw)

        # Find the reference row (lookback periods ago)
        ref_idx = i - lookback
        if ref_idx < 0:
            # Not enough history
            output_rows.append({
                "period":       period,
                "actual_spend": f"{spend:.1f}",
                "growth_pct":   "N/A (no prior period)",
                "formula":      formula_template,
                "null_flag":    "FALSE",
                "null_reason":  "",
            })
            continue

        ref_row      = filtered[ref_idx]
        ref_spend_raw = ref_row["actual_spend"].strip()

        if ref_spend_raw == "":
            # Reference period itself is null — cannot compute growth
            output_rows.append({
                "period":       period,
                "actual_spend": f"{spend:.1f}",
                "growth_pct":   "N/A (prior period is NULL)",
                "formula":      formula_template,
                "null_flag":    "FALSE",
                "null_reason":  "",
            })
            continue

        ref_spend = float(ref_spend_raw)

        if ref_spend == 0:
            growth_pct_str = "N/A (prior period spend = 0)"
        else:
            growth_pct = ((spend - ref_spend) / ref_spend) * 100
            sign = "+" if growth_pct >= 0 else ""
            growth_pct_str = f"{sign}{growth_pct:.1f}%"

        output_rows.append({
            "period":       period,
            "actual_spend": f"{spend:.1f}",
            "growth_pct":   growth_pct_str,
            "formula":      formula_template,
            "null_flag":    "FALSE",
            "null_reason":  "",
        })

    return output_rows


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category",    required=True,  help="Category name, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True,  help="Growth type: MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write output CSV")
    args = parser.parse_args()

    growth_type = args.growth_type.strip()

    # Enforcement: refuse if growth-type is not valid
    if growth_type not in ("MoM", "YoY"):
        sys.exit(
            "ERROR: --growth-type must be either 'MoM' or 'YoY'. "
            "You provided: '" + growth_type + "'. Please specify which growth calculation you need."
        )

    # Skill 1 — Load and validate data
    print(f"\nLoading dataset from: {args.input}")
    all_rows, null_rows = load_dataset(args.input)
    print(f"Dataset loaded: {len(all_rows)} total rows.")

    # Enforcement: report null rows BEFORE computing
    if null_rows:
        print(f"\nWARNING: {len(null_rows)} null actual_spend rows detected and flagged:")
        for nr in null_rows:
            print(f"   - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
    else:
        print("No null rows found in dataset.")

    # Skill 2 — Compute growth
    print(f"\nComputing {growth_type} growth for:")
    print(f"   Ward     : {args.ward}")
    print(f"   Category : {args.category}")

    results = compute_growth(all_rows, args.ward, args.category, growth_type)

    # Write output CSV
    fieldnames = ["period", "actual_spend", "growth_pct", "formula", "null_flag", "null_reason"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nDone. Results written to: {args.output}")
    print(f"Total output rows: {len(results)}")


if __name__ == "__main__":
    main()
