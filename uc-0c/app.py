"""
UC-0C — Number That Looks Right
Implemented using agents.md (RICE) and skills.md contracts.

Failure modes guarded against:
  - Wrong aggregation level  (agents.md rule 1)
  - Silent null handling     (agents.md rule 2)
  - Formula assumption       (agents.md rules 3 & 4)
"""
import argparse
import csv
import sys

# ---------------------------------------------------------------------------
# Required columns — skills.md load_dataset contract
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

VALID_GROWTH_TYPES = {"MoM", "YoY"}


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, surface every null actual_spend
    row (with verbatim notes reason) before returning.

    Output dict:
      - data:              list of row dicts (all rows, unmodified)
      - null_rows:         list of {period, ward, category, null_reason}
      - null_count:        int
      - columns_validated: bool

    Raises FileNotFoundError if file cannot be read.
    Raises ValueError if required columns are missing or actual_spend absent.
    """
    try:
        f = open(file_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}\n"
            "Check the path and try again."
        )

    with f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])

        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}\n"
                "Cannot proceed with an incomplete dataset."
            )

        data = list(reader)

    if not data:
        raise ValueError("Dataset is empty — no rows found.")

    # Detect null actual_spend rows — flag before any computation (agents.md rule 2)
    null_rows = []
    for row in data:
        val = row.get("actual_spend", "").strip()
        if val == "" or val.lower() == "null":
            null_rows.append({
                "period":      row.get("period", "").strip(),
                "ward":        row.get("ward", "").strip(),
                "category":    row.get("category", "").strip(),
                "null_reason": row.get("notes", "").strip() or "No reason provided in notes column",
            })

    return {
        "data":              data,
        "null_rows":         null_rows,
        "null_count":        len(null_rows),
        "columns_validated": True,
    }


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for a specific ward + category.

    Returns a list of dicts (one per period) each with:
      period, actual_spend, growth_pct, formula, flag

    Raises ValueError on: invalid growth_type, missing ward/category args,
    no matching rows, refusal for cross-ward/category aggregation.
    """
    # agents.md rule 4 — refuse if growth_type not specified or invalid
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            "Growth type not specified — please provide "
            "--growth-type MoM or --growth-type YoY."
        )

    # agents.md rule 1 — refuse aggregation when ward or category is missing
    if not ward or not category:
        raise ValueError(
            "Aggregation across wards/categories not permitted without explicit "
            "instruction — please specify a ward and category."
        )

    # Build a lookup of null rows for fast flagging (period+ward+category key)
    null_lookup = {
        (nr["period"], nr["ward"], nr["category"]): nr["null_reason"]
        for nr in dataset["null_rows"]
    }

    # Filter rows to the requested ward + category (agents.md rule 1)
    rows = [
        r for r in dataset["data"]
        if r["ward"].strip() == ward and r["category"].strip() == category
    ]

    if not rows:
        raise ValueError(
            f"No rows found for ward='{ward}' category='{category}' — "
            "check exact spelling."
        )

    # Sort by period (YYYY-MM sorts lexicographically correctly)
    rows = sorted(rows, key=lambda r: r["period"].strip())

    # Parse actual_spend — null rows get None
    def parse_spend(r):
        val = r.get("actual_spend", "").strip()
        if val == "" or val.lower() == "null":
            return None
        try:
            return float(val)
        except ValueError:
            return None

    parsed = [(r["period"].strip(), parse_spend(r)) for r in rows]

    results = []

    for i, (period, spend) in enumerate(parsed):
        key = (period, ward, category)
        null_reason = null_lookup.get(key)

        # agents.md rule 2 — flag null rows, never compute growth for them
        if spend is None:
            results.append({
                "period":       period,
                "actual_spend": None,
                "growth_pct":   None,
                "formula":      None,
                "flag":         f"NULL — {null_reason or 'actual_spend missing'}",
            })
            continue

        # Determine comparison period
        if growth_type == "MoM":
            prev_period, prev_spend = parsed[i - 1] if i > 0 else (None, None)
            formula_template = "MoM: (({cur} - {prev}) / {prev}) × 100"
        else:  # YoY
            # Find same month, prior year
            yoy_period = f"{int(period[:4]) - 1}{period[4:]}"
            prior = next((s for p, s in parsed if p == yoy_period), None)
            prev_spend = prior
            formula_template = "YoY: (({cur} - {prev}) / {prev}) × 100"

        # No prior period available
        if prev_spend is None or (growth_type == "MoM" and i == 0):
            results.append({
                "period":       period,
                "actual_spend": spend,
                "growth_pct":   None,
                "formula":      "No prior period — growth cannot be computed.",
                "flag":         "",
            })
            continue

        # Compute growth — agents.md rule 3: formula shown in every row
        growth = ((spend - prev_spend) / prev_spend) * 100
        formula_str = (
            formula_template.format(cur=spend, prev=prev_spend)
            + f" = {growth:+.1f}%"
        )

        results.append({
            "period":       period,
            "actual_spend": spend,
            "growth_pct":   round(growth, 1),
            "formula":      formula_str,
            "flag":         "",
        })

    return results


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _print_null_report(null_rows: list) -> None:
    """Print flagged null rows to stdout before results (agents.md rule 2)."""
    if not null_rows:
        return
    print(f"\n⚠  {len(null_rows)} NULL actual_spend row(s) detected — growth not computed for these:\n")
    for nr in null_rows:
        print(f"  [{nr['period']}] {nr['ward']} / {nr['category']}")
        print(f"    Reason: {nr['null_reason']}")
    print()


def _write_output(results: list, output_path: str, ward: str, category: str,
                  growth_type: str) -> None:
    """Write per-period growth table to CSV."""
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({
                "period":       row["period"],
                "ward":         ward,
                "category":     category,
                "actual_spend": "" if row["actual_spend"] is None else row["actual_spend"],
                "growth_pct":   "" if row["growth_pct"] is None else row["growth_pct"],
                "formula":      row["formula"] or "",
                "flag":         row["flag"],
            })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=True,  dest="growth_type",
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-on-month) or YoY (year-on-year)")
    parser.add_argument("--output",      required=True,  help="Path to write results CSV")
    args = parser.parse_args()

    # Skill 1: load and validate — null rows reported first (agents.md rule 2)
    dataset = load_dataset(args.input)
    _print_null_report(dataset["null_rows"])

    # Skill 2: compute growth
    try:
        results = compute_growth(
            dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    _write_output(results, args.output, args.ward, args.category, args.growth_type)
    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
