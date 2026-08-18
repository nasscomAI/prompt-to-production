"""
UC-0C app.py — Budget Growth Analysis Agent
Implements load_dataset and compute_growth skills per agents.md + skills.md.

Run:
  python app.py \
    --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 - Kasba" \
    --category "Roads & Pothole Repair" \
    --growth-type MoM \
    --output growth_output.csv

Ward and category arguments support partial (case-insensitive) matching.
"""
import argparse
import csv


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate required columns, and report every null
    actual_spend row before returning data.

    Returns:
        {
          "null_report": [ {period, ward, category, notes}, ... ],
          "data":        [ {period, ward, category, budgeted_amount,
                            actual_spend, notes}, ... ]
        }
    actual_spend is stored as float or None — never coerced to 0.
    """
    required = {"period", "ward", "category", "budgeted_amount",
                "actual_spend", "notes"}

    try:
        with open(file_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ValueError("Dataset file is empty — cannot proceed.")
            missing = required - {c.strip() for c in reader.fieldnames}
            if missing:
                raise ValueError(
                    f"Required column(s) missing from CSV: {sorted(missing)}"
                )
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    if not rows:
        raise ValueError("Dataset has zero data rows — cannot proceed.")

    data = []
    null_report = []

    for row in rows:
        raw = row.get("actual_spend", "").strip()
        actual = None if raw == "" else float(raw)
        record = {
            "period":           row["period"].strip(),
            "ward":             row["ward"].strip(),
            "category":         row["category"].strip(),
            "budgeted_amount":  float(row["budgeted_amount"].strip()),
            "actual_spend":     actual,
            "notes":            row.get("notes", "").strip(),
        }
        data.append(record)
        if actual is None:
            null_report.append({
                "period":   record["period"],
                "ward":     record["ward"],
                "category": record["category"],
                "notes":    record["notes"] or "(no reason given in notes column)",
            })

    return {"null_report": null_report, "data": data}


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(data: list, ward: str, category: str,
                   growth_type: str) -> list:
    """
    Filter data to the exact ward+category slice, then compute MoM or YoY
    growth for every period. Every output row includes an explicit formula.

    Flags:
      FIRST_PERIOD_NO_PRIOR      — first row, no predecessor
      NULL_NOT_COMPUTED          — this row's actual_spend is None
      PRIOR_NULL_NOT_COMPUTED    — prior row's actual_spend is None
      OK                         — growth computed successfully
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "Growth type not specified. "
            "Please rerun with --growth-type MoM or --growth-type YoY."
        )

    # Partial, case-insensitive match for ward and category
    slice_ = [
        r for r in data
        if ward.lower() in r["ward"].lower()
        and category.lower() in r["category"].lower()
    ]

    if not slice_:
        raise ValueError(
            f"No rows found matching ward='{ward}' and category='{category}'. "
            "Check spelling or use a substring of the full name."
        )

    # Detect multiple distinct wards or categories in the slice
    distinct_wards = {r["ward"] for r in slice_}
    distinct_cats  = {r["category"] for r in slice_}
    if len(distinct_wards) > 1 or len(distinct_cats) > 1:
        raise ValueError(
            "Aggregation across wards or categories is not permitted. "
            "Specify a single ward and a single category using --ward and --category.\n"
            f"  Matched wards     : {sorted(distinct_wards)}\n"
            f"  Matched categories: {sorted(distinct_cats)}"
        )

    matched_ward     = next(iter(distinct_wards))
    matched_category = next(iter(distinct_cats))

    slice_.sort(key=lambda r: r["period"])
    results = []

    for i, row in enumerate(slice_):
        period  = row["period"]
        actual  = row["actual_spend"]
        notes   = row["notes"]

        # Determine prior row
        if growth_type == "MoM":
            prior_row = slice_[i - 1] if i > 0 else None
        else:  # YoY — find the same month in the prior year
            prior_period = f"{int(period[:4]) - 1}{period[4:]}"
            prior_candidates = [r for r in slice_ if r["period"] == prior_period]
            prior_row = prior_candidates[0] if prior_candidates else None

        # Build output row
        if i == 0 and growth_type == "MoM":
            results.append({
                "period":         period,
                "ward":           matched_ward,
                "category":       matched_category,
                "actual_spend":   actual,
                "prior_period":   None,
                "prior_spend":    None,
                "formula":        "First period — no prior value available",
                "growth_pct":     None,
                "flag":           "FIRST_PERIOD_NO_PRIOR",
            })
            continue

        if actual is None:
            results.append({
                "period":         period,
                "ward":           matched_ward,
                "category":       matched_category,
                "actual_spend":   None,
                "prior_period":   prior_row["period"] if prior_row else None,
                "prior_spend":    prior_row["actual_spend"] if prior_row else None,
                "formula":        f"NULL — {notes}",
                "growth_pct":     None,
                "flag":           f"NULL_NOT_COMPUTED: {notes}",
            })
            continue

        if prior_row is None:
            results.append({
                "period":         period,
                "ward":           matched_ward,
                "category":       matched_category,
                "actual_spend":   actual,
                "prior_period":   None,
                "prior_spend":    None,
                "formula":        "No prior period available for growth calculation",
                "growth_pct":     None,
                "flag":           "FIRST_PERIOD_NO_PRIOR",
            })
            continue

        prior_spend = prior_row["actual_spend"]

        if prior_spend is None:
            prior_notes = prior_row["notes"]
            results.append({
                "period":         period,
                "ward":           matched_ward,
                "category":       matched_category,
                "actual_spend":   actual,
                "prior_period":   prior_row["period"],
                "prior_spend":    None,
                "formula":        f"Prior period {prior_row['period']} is NULL — {prior_notes}",
                "growth_pct":     None,
                "flag":           f"PRIOR_NULL_NOT_COMPUTED: prior {prior_row['period']} null — {prior_notes}",
            })
            continue

        pct = (actual - prior_spend) / prior_spend * 100
        sign = "+" if pct >= 0 else ""
        formula = (
            f"({actual} − {prior_spend}) / {prior_spend} × 100 "
            f"= {sign}{round(pct, 1)}%"
        )
        results.append({
            "period":         period,
            "ward":           matched_ward,
            "category":       matched_category,
            "actual_spend":   actual,
            "prior_period":   prior_row["period"],
            "prior_spend":    prior_spend,
            "formula":        formula,
            "growth_pct":     round(pct, 1),
            "flag":           "OK",
        })

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analysis Agent"
    )
    parser.add_argument("--input",       required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,
                        help="Ward name or substring (case-insensitive)")
    parser.add_argument("--category",    required=True,
                        help="Category name or substring (case-insensitive)")
    parser.add_argument("--growth-type", required=True,
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM or YoY")
    parser.add_argument("--output",      required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    # --- Step 1: load and report nulls ---
    print(f"\nLoading dataset: {args.input}")
    dataset = load_dataset(args.input)

    print(f"\nDataset loaded — {len(dataset['data'])} rows total.")
    print(f"NULL actual_spend rows found: {len(dataset['null_report'])}")
    if dataset["null_report"]:
        print("\n  NULL ROW REPORT (mandatory pre-computation disclosure):")
        print(f"  {'Period':<10} {'Ward':<30} {'Category':<30} {'Reason'}")
        print("  " + "-" * 90)
        for nr in dataset["null_report"]:
            print(f"  {nr['period']:<10} {nr['ward']:<30} {nr['category']:<30} {nr['notes']}")

    # --- Step 2: compute growth ---
    print(f"\nComputing {args.growth_type} growth for "
          f"ward='{args.ward}' / category='{args.category}' ...")
    results = compute_growth(
        data=dataset["data"],
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    # --- Step 3: write output CSV ---
    fieldnames = [
        "period", "ward", "category", "actual_spend",
        "prior_period", "prior_spend", "formula", "growth_pct", "flag",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nOutput written to: {args.output}")

    # --- Step 4: print results table to stdout ---
    print(f"\n{'Period':<10} {'Actual':>8} {'Prior':>8} {'Growth':>9}  {'Flag':<35} Formula")
    print("-" * 110)
    for r in results:
        actual_s  = f"{r['actual_spend']}" if r["actual_spend"] is not None else "NULL"
        prior_s   = f"{r['prior_spend']}"  if r["prior_spend"]  is not None else "—"
        growth_s  = (f"{'+' if r['growth_pct'] >= 0 else ''}{r['growth_pct']}%"
                     if r["growth_pct"] is not None else "—")
        print(f"{r['period']:<10} {actual_s:>8} {prior_s:>8} {growth_s:>9}  "
              f"{r['flag']:<35} {r['formula']}")


if __name__ == "__main__":
    main()

