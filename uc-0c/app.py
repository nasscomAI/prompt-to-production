"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ("MoM", "YoY")


class AgentRefusal(Exception):
    """Raised whenever the agent must refuse rather than guess or aggregate."""
    pass


# ---------------------------------------------------------------------------
# Skill 1: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(path):
    """
    Reads the ward budget CSV, validates its columns, and reports the null
    count and specific null rows before returning the data.

    Returns:
        (rows, null_report) where:
          rows        = list of dict records (raw strings, actual_spend may be "")
          null_report = list of dicts describing each null actual_spend row
                        with period, ward, category, and notes reason.

    Error handling:
      - Missing/malformed required columns -> refuse (AgentRefusal), report which.
      - File not found / unreadable -> refuse (AgentRefusal), report the path issue.
      - Null actual_spend values are never dropped or silently filled — every
        null row is captured in null_report before the dataset is returned.
    """
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                raise AgentRefusal(
                    f"Cannot load dataset — missing required column(s): {missing}. "
                    f"Found columns: {fieldnames}"
                )
            rows = list(reader)
    except FileNotFoundError:
        raise AgentRefusal(f"Cannot load dataset — file not found at path: {path}")
    except OSError as e:
        raise AgentRefusal(f"Cannot load dataset — unable to read file at {path}: {e}")

    null_report = []
    for row in rows:
        spend = (row.get("actual_spend") or "").strip()
        if spend == "":
            null_report.append({
                "period": row.get("period", ""),
                "ward": row.get("ward", ""),
                "category": row.get("category", ""),
                "reason": row.get("notes", "").strip() or "(no reason given in notes column)",
            })

    print(f"[load_dataset] Loaded {len(rows)} rows from {path}")
    print(f"[load_dataset] Found {len(null_report)} row(s) with null actual_spend:")
    for n in null_report:
        print(f"  - {n['period']} | {n['ward']} | {n['category']} | reason: {n['reason']}")

    return rows, null_report


# ---------------------------------------------------------------------------
# Skill 2: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(rows, null_report, ward, category, growth_type):
    """
    Takes ward + category + growth_type and returns a per-period table with
    the formula shown for every row.

    Returns:
        list of dict records, one per period for the given ward/category, each
        containing: period, actual_spend, growth, formula, flag

    Error handling:
      - growth_type not specified -> refuse (AgentRefusal), ask user to choose MoM/YoY.
      - ward or category missing / matches nothing -> refuse (AgentRefusal).
      - Never aggregates across wards or categories: operates strictly on the
        single ward+category slice requested.
      - Null actual_spend rows are never computed — they are flagged with the
        reason from notes instead.
    """
    if not growth_type:
        raise AgentRefusal(
            "No --growth-type specified. I cannot guess whether you want MoM or "
            "YoY growth. Please re-run with --growth-type MoM or --growth-type YoY."
        )
    if growth_type not in VALID_GROWTH_TYPES:
        raise AgentRefusal(
            f"Invalid --growth-type '{growth_type}'. Must be one of {VALID_GROWTH_TYPES}."
        )
    if not ward or not category:
        raise AgentRefusal(
            "A specific --ward and --category are required. Refusing to compute "
            "growth across all wards/categories (would be an unauthorized aggregation)."
        )

    subset = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    if not subset:
        raise AgentRefusal(
            f"No rows found for ward='{ward}' and category='{category}'. "
            "Refusing to guess a close match or fall back to an aggregate view."
        )

    subset.sort(key=lambda r: r["period"])

    # Build a quick lookup of null reasons for this ward/category
    null_lookup = {
        (n["period"], n["ward"], n["category"]): n["reason"]
        for n in null_report
    }

    def get_spend(period):
        for r in subset:
            if r["period"] == period:
                v = (r.get("actual_spend") or "").strip()
                return float(v) if v != "" else None
        return None

    def prior_period(period, growth_type):
        year, month = period.split("-")
        year, month = int(year), int(month)
        if growth_type == "MoM":
            if month == 1:
                return None  # no prior month in dataset (Jan 2024 is first)
            return f"{year}-{month-1:02d}"
        else:  # YoY
            return f"{year-1}-{month:02d}"

    results = []
    for row in subset:
        period = row["period"]
        spend_str = (row.get("actual_spend") or "").strip()
        key = (period, ward, category)

        if key in null_lookup:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_pct": "",
                "formula": "N/A — actual_spend is null, not computed",
                "flag": f"NULL — {null_lookup[key]}",
            })
            continue

        current = float(spend_str) if spend_str != "" else None
        prev_period = prior_period(period, growth_type)
        prev = get_spend(prev_period) if prev_period else None

        if current is None:
            # Shouldn't normally hit this since null_lookup should have caught it,
            # but guard anyway rather than silently treating as zero.
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": "", "growth_pct": "",
                "formula": "N/A — actual_spend missing",
                "flag": "NULL — reason not found in notes column",
            })
            continue

        if prev_period is None or prev is None:
            reason = "no prior period available in dataset" if prev_period is None \
                else f"prior period {prev_period} actual_spend is null/unavailable"
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": current, "growth_pct": "",
                "formula": f"({growth_type}) requires prior period value — unavailable ({reason})",
                "flag": f"NOT COMPUTED — {reason}",
            })
            continue

        growth_pct = ((current - prev) / prev) * 100
        formula = f"(actual_spend[{period}] - actual_spend[{prev_period}]) / actual_spend[{prev_period}] * 100 = ({current} - {prev}) / {prev} * 100 = {growth_pct:.1f}%"
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current,
            "growth_pct": f"{growth_pct:.1f}%",
            "formula": formula,
            "flag": "",
        })

    return results


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------
def write_output(results, output_path):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"[compute_growth] Wrote {len(results)} row(s) to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="UC-0C — per-ward per-category budget growth agent."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Ward name (required)")
    parser.add_argument("--category", required=False, default=None, help="Category name (required)")
    parser.add_argument(
        "--growth-type", dest="growth_type", required=False, default=None,
        choices=VALID_GROWTH_TYPES,
        help="MoM or YoY. If omitted, the agent will refuse rather than guess."
    )
    parser.add_argument("--output", required=False, default="growth_output.csv",
                         help="Output CSV path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    try:
        rows, null_report = load_dataset(args.input)

        # Enforcement: never aggregate across wards/categories unless explicitly
        # instructed — a missing ward or category is treated as an implicit
        # "all wards / all categories" request and must be refused.
        if not args.ward or not args.category:
            raise AgentRefusal(
                "Both --ward and --category must be explicitly specified. "
                "Refusing to compute an all-ward or all-category aggregation."
            )

        results = compute_growth(rows, null_report, args.ward, args.category, args.growth_type)
        write_output(results, args.output)

    except AgentRefusal as e:
        print(f"[REFUSED] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()