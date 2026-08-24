"""
UC-0C — Data / Growth Analysis
Implementation guided by agents.md (RICE framework) and skills.md.

Design: Pure-Python CSV analysis — no LLM dependency.
Strict per-ward per-category scoping. All nulls are flagged before computation.
Every formula is shown explicitly in the output. Growth type must be specified.
"""
from __future__ import annotations
import argparse
import csv
import io
import sys
from pathlib import Path

# Ensure stdout/stderr use UTF-8 on Windows to avoid cp1252 encoding errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")



# ── skill: load_dataset ───────────────────────────────────────────────────────
def load_dataset(
    file_path: str,
    ward: str | None = None,
    category: str | None = None,
) -> dict:
    """
    Load and validate ward_budget.csv. Report all nulls before returning data.
    Returns dict with keys: data, null_report, total_rows, null_count.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    required_columns = {"period", "ward", "category", "actual_spend", "notes"}

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        if reader.fieldnames:
            found_cols = {c.strip() for c in reader.fieldnames}
        else:
            found_cols = set()

    missing = required_columns - found_cols
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Apply ward and category filters
    filtered = all_rows
    if ward:
        filtered = [r for r in filtered if r["ward"].strip() == ward.strip()]
    if category:
        filtered = [r for r in filtered if r["category"].strip() == category.strip()]

    if not filtered:
        filter_desc = []
        if ward:
            filter_desc.append(f"ward='{ward}'")
        if category:
            filter_desc.append(f"category='{category}'")
        raise ValueError(
            f"No rows match filter: {', '.join(filter_desc)}. "
            "Check spelling and exact string values."
        )

    # Report null rows
    null_report = []
    for row in filtered:
        spend_raw = row.get("actual_spend", "").strip()
        if spend_raw == "" or spend_raw.lower() == "null":
            null_report.append({
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "notes": row.get("notes", "").strip(),
            })

    if null_report:
        print("=" * 60)
        print(f"NULL REPORT — {len(null_report)} null actual_spend row(s) detected:")
        for nr in null_report:
            print(
                f"  {nr['period']} | {nr['ward']} | {nr['category']}"
                + (f" | NOTE: {nr['notes']}" if nr["notes"] else "")
            )
        print("These rows will appear in output with growth_pct = NULL.")
        print("=" * 60)
    else:
        print("NULL REPORT — No null actual_spend rows in this filtered dataset.")

    return {
        "data": filtered,
        "null_report": null_report,
        "total_rows": len(filtered),
        "null_count": len(null_report),
    }


# ── skill: compute_growth ─────────────────────────────────────────────────────
def compute_growth(
    data: list[dict],
    growth_type: str,
    ward: str,
    category: str,
) -> list[dict]:
    """
    Compute MoM or YoY growth per period for the given ward+category subset.
    Returns a list of result dicts. Refuses if growth_type is ambiguous.
    """
    if growth_type not in ("MoM", "YoY"):
        return [{"error": "growth_type must be MoM or YoY — refusing to guess"}]

    # Sort by period
    sorted_data = sorted(data, key=lambda r: r["period"].strip())
    if len(sorted_data) < 2:
        return [{"error": "Insufficient data — need at least 2 periods to compute growth"}]

    # Build a quick lookup: period → actual_spend (float or None)
    spend_map: dict[str, float | None] = {}
    notes_map: dict[str, str] = {}
    for row in sorted_data:
        period = row["period"].strip()
        spend_raw = row.get("actual_spend", "").strip()
        notes_map[period] = row.get("notes", "").strip()
        if spend_raw == "" or spend_raw.lower() == "null":
            spend_map[period] = None
        else:
            spend_map[period] = float(spend_raw)

    periods = [r["period"].strip() for r in sorted_data]

    results = []
    for idx, period in enumerate(periods):
        current_spend = spend_map[period]
        null_flag = notes_map[period] if current_spend is None else ""

        if growth_type == "MoM":
            if idx == 0:
                prev_period = None
                prev_spend = None
            else:
                prev_period = periods[idx - 1]
                prev_spend = spend_map[prev_period]
        else:  # YoY
            # Find same month prior year
            parts = period.split("-")
            prior_year_period = f"{int(parts[0]) - 1}-{parts[1]}"
            prev_period = prior_year_period if prior_year_period in spend_map else None
            prev_spend = spend_map.get(prior_year_period) if prev_period else None

        # Compute growth
        if idx == 0 and growth_type == "MoM":
            growth_pct = None
            formula = "First period — no previous period available"
        elif prev_period is None:
            growth_pct = None
            formula = f"No prior {growth_type} period found"
        elif current_spend is None or prev_spend is None:
            growth_pct = None
            if current_spend is None and prev_spend is None:
                formula = "Both current and previous period are NULL"
            elif current_spend is None:
                formula = f"Current period ({period}) is NULL — cannot compute"
            else:
                formula = f"Previous period ({prev_period}) is NULL — cannot compute"
        else:
            growth_pct = round((current_spend - prev_spend) / prev_spend * 100, 1)
            formula = (
                f"({current_spend} - {prev_spend}) / {prev_spend} × 100"
                f" = {growth_pct:+.1f}%"
            )

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend,
            "prev_period": prev_period,
            "prev_spend": prev_spend,
            "growth_pct": growth_pct,
            "formula": formula,
            "null_flag": null_flag,
        })

    return results


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            '  python app.py --input ../data/budget/ward_budget.csv \\\n'
            '    --ward "Ward 1 \u2013 Kasba" \\\n'
            '    --category "Roads & Pothole Repair" \\\n'
            '    --growth-type MoM \\\n'
            '    --output growth_output.csv'
        ),
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",  default=None, help="Exact ward name (required)")
    parser.add_argument("--category", default=None, help="Exact category name (required)")
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        default=None,
        help="MoM or YoY (required — not guessed)",
    )
    parser.add_argument("--output", required=True, help="Path for growth_output.csv")
    args = parser.parse_args()

    # Enforcement: ward and category must be specified
    if not args.ward or not args.category:
        print(
            "ERROR: --ward and --category are required. "
            "Cross-ward or all-category queries are not permitted.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Enforcement: growth_type must be specified
    if not args.growth_type:
        print(
            "ERROR: --growth-type is required. "
            "Please specify MoM or YoY. Guessing is not permitted.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: --growth-type must be exactly 'MoM' or 'YoY', "
            f"got '{args.growth_type}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Loading dataset: {args.input}")
    print(f"Scope: ward='{args.ward}' | category='{args.category}'")
    print(f"Growth type: {args.growth_type}")
    print()

    dataset = load_dataset(args.input, ward=args.ward, category=args.category)
    print(f"\nFiltered rows: {dataset['total_rows']} | Nulls: {dataset['null_count']}\n")

    results = compute_growth(
        dataset["data"],
        growth_type=args.growth_type,
        ward=args.ward,
        category=args.category,
    )

    # Check for error return
    if len(results) == 1 and "error" in results[0]:
        print(f"ERROR: {results[0]['error']}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV
    fieldnames = [
        "period", "ward", "category", "actual_spend",
        "prev_period", "prev_spend", "growth_pct", "formula", "null_flag",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to: {args.output}")
    print(f"Rows in output: {len(results)}")

    # Print verification spot-check
    print("\n-- Spot-check (reference values from README) --")
    for row in results:
        period = row.get("period", "")
        if period in ("2024-07", "2024-10"):
            gp = row.get("growth_pct")
            print(
                f"  {period}: actual_spend={row.get('actual_spend')} | "
                f"MoM growth={f'{gp:+.1f}%' if gp is not None else 'NULL'} | "
                f"formula: {row.get('formula')}"
            )
