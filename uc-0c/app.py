"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth per agents.md (RICE) and skills.md.

Core failure modes guarded against:
  - Wrong aggregation level : refuse any cross-ward or cross-category request
  - Silent null handling     : all null rows reported before computation begins
  - Formula assumption       : every output row shows exact formula with values
  - Growth-type guessing     : refuse if --growth-type not supplied; never default
"""
import argparse
import csv
import os
import unicodedata


def _normalize(s: str) -> str:
    """Normalize string for comparison: collapse unicode dashes and whitespace."""
    # Replace en-dash, em-dash, figure dash, horizontal bar → hyphen
    s = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2012", "-").replace("\u2015", "-")
    # Normalize unicode to NFC and collapse whitespace
    s = unicodedata.normalize("NFC", s).strip()
    return s

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
AGGREGATION_REFUSAL = (
    "Cross-ward or cross-category aggregation is not permitted. "
    "Please specify a single ward and category."
)
GROWTH_TYPE_REFUSAL = (
    "Growth type not specified. "
    "Please provide --growth-type MoM or --growth-type YoY. "
    "Never guess or default silently."
)


# ---------------------------------------------------------------------------
# Skill 1: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, report all null actual_spend rows,
    then return {rows, null_rows}.
    Null report is printed to stdout before any computation can proceed.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    with open(file_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
            found = reader.fieldnames or []
            missing = REQUIRED_COLUMNS - set(found)
            raise ValueError(
                f"Required columns missing from CSV: {sorted(missing)}. "
                f"Columns found: {found}"
            )
        rows = list(reader)

    # Parse actual_spend to float where possible; collect nulls
    parsed_rows = []
    null_rows = []
    for row in rows:
        raw = row["actual_spend"].strip()
        if raw == "":
            row["_spend_float"] = None
            reason = row["notes"].strip() or "(no reason given in source data)"
            null_rows.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "notes":    reason,
            })
        else:
            try:
                row["_spend_float"] = float(raw)
            except ValueError:
                row["_spend_float"] = None
                reason = row["notes"].strip() or "(no reason given in source data)"
                null_rows.append({
                    "period":   row["period"],
                    "ward":     row["ward"],
                    "category": row["category"],
                    "notes":    reason,
                })
        parsed_rows.append(row)

    # RICE enforcement: report nulls before any computation
    print(f"Null actual_spend rows found: {len(null_rows)}")
    for nr in null_rows:
        print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['notes']}")
    if null_rows:
        print("  ^ These rows will be flagged N/A in growth output — not computed.")
    print()

    return {"rows": parsed_rows, "null_rows": null_rows}


# ---------------------------------------------------------------------------
# Skill 2: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute MoM or YoY growth for a single ward + category combination.
    Every output row includes the exact formula with values.
    Null rows are flagged — never filled or skipped.
    Aggregation requests are refused.
    """
    # RICE enforcement: refuse aggregation attempts
    if not ward or ward.strip().lower() in ("*", "all", ""):
        raise ValueError(AGGREGATION_REFUSAL)
    if not category or category.strip().lower() in ("*", "all", ""):
        raise ValueError(AGGREGATION_REFUSAL)

    # RICE enforcement: refuse if growth_type not specified
    if not growth_type or growth_type.strip() not in ("MoM", "YoY"):
        raise ValueError(GROWTH_TYPE_REFUSAL)

    # Filter to exact ward + category (normalized for dash/encoding variants)
    norm_ward = _normalize(ward)
    norm_cat  = _normalize(category)
    subset = [
        r for r in rows
        if _normalize(r["ward"]) == norm_ward
        and _normalize(r["category"]) == norm_cat
    ]

    if not subset:
        # Report what is actually available
        distinct_wards = sorted(set(r["ward"] for r in rows))
        distinct_cats  = sorted(set(r["category"] for r in rows))
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'.\n"
            f"Available wards: {distinct_wards}\n"
            f"Available categories: {distinct_cats}"
        )

    # Sort chronologically by period (YYYY-MM sorts lexicographically)
    subset.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(subset):
        period = row["period"]
        spend  = row["_spend_float"]

        # Null row — cannot compute
        if spend is None:
            reason = row["notes"].strip() or "(no reason given in source data)"
            results.append({
                "period":       period,
                "actual_spend": "NULL",
                "growth":       "N/A",
                "formula":      f"N/A — null actual_spend (reason: {reason})",
            })
            continue

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period":       period,
                    "actual_spend": spend,
                    "growth":       "N/A",
                    "formula":      "N/A — first period, no prior value",
                })
                continue

            prev_row   = subset[i - 1]
            prev_spend = prev_row["_spend_float"]

            if prev_spend is None:
                prev_reason = prev_row["notes"].strip() or "(no reason given)"
                results.append({
                    "period":       period,
                    "actual_spend": spend,
                    "growth":       "N/A",
                    "formula":      f"N/A — previous period ({prev_row['period']}) was null (reason: {prev_reason})",
                })
                continue

            if prev_spend == 0:
                results.append({
                    "period":       period,
                    "actual_spend": spend,
                    "growth":       "N/A",
                    "formula":      f"N/A — previous period spend was 0, division undefined",
                })
                continue

            pct = (spend - prev_spend) / prev_spend * 100
            sign = "+" if pct >= 0 else ""
            results.append({
                "period":       period,
                "actual_spend": spend,
                "growth":       f"{sign}{pct:.1f}%",
                "formula":      (
                    f"MoM = ({spend} - {prev_spend}) / {prev_spend} × 100 "
                    f"= {sign}{pct:.1f}%"
                ),
            })

        else:  # YoY
            # Find same month in prior year
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
            prior_rows = [r for r in subset if r["period"] == prior_period]

            if not prior_rows:
                results.append({
                    "period":       period,
                    "actual_spend": spend,
                    "growth":       "N/A",
                    "formula":      f"N/A — no data for prior year period ({prior_period})",
                })
                continue

            prior_spend = prior_rows[0]["_spend_float"]
            if prior_spend is None:
                prior_reason = prior_rows[0]["notes"].strip() or "(no reason given)"
                results.append({
                    "period":       period,
                    "actual_spend": spend,
                    "growth":       "N/A",
                    "formula":      f"N/A — prior year period ({prior_period}) was null (reason: {prior_reason})",
                })
                continue

            if prior_spend == 0:
                results.append({
                    "period":       period,
                    "actual_spend": spend,
                    "growth":       "N/A",
                    "formula":      f"N/A — prior year spend was 0, division undefined",
                })
                continue

            pct = (spend - prior_spend) / prior_spend * 100
            sign = "+" if pct >= 0 else ""
            results.append({
                "period":       period,
                "actual_spend": spend,
                "growth":       f"{sign}{pct:.1f}%",
                "formula":      (
                    f"YoY = ({spend} - {prior_spend}) / {prior_spend} × 100 "
                    f"= {sign}{pct:.1f}%"
                ),
            })

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=False, dest="growth_type",
                        help="MoM or YoY — required; will refuse if omitted")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # RICE enforcement: refuse if growth-type not provided
    if not args.growth_type:
        print(f"ERROR: {GROWTH_TYPE_REFUSAL}")
        raise SystemExit(1)

    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset['rows'])} rows.")
    print(f"Computing {args.growth_type} growth for: {args.ward} | {args.category}\n")

    results = compute_growth(
        dataset["rows"],
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    # Write output CSV
    fieldnames = ["period", "actual_spend", "growth", "formula"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary table to stdout
    print(f"{'Period':<10} {'Actual Spend':>14} {'Growth':>10}  Formula")
    print("-" * 80)
    for r in results:
        spend_str = f"{r['actual_spend']} lakh" if r["actual_spend"] != "NULL" else "NULL"
        print(f"{r['period']:<10} {spend_str:>14} {r['growth']:>10}  {r['formula']}")

    print(f"\nDone. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()
