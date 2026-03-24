"""
UC-0C — Number That Looks Right: Budget Growth Analyser
Computes per-ward per-category MoM or YoY growth from ward_budget.csv.

Enforcement rules from agents.md:
1. Never aggregate across wards or categories — refuse if requested.
2. Report all null actual_spend rows before computing (never silently skip).
3. Show formula for every computed growth row.
4. Refuse if --growth-type not provided.

Run command:
    python app.py \
      --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 - Kasba" \
      --category "Roads & Pothole Repair" \
      --growth-type MoM \
      --output growth_output.csv
"""
import argparse
import csv
import sys
from typing import Optional


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str, ward: str, category: str) -> tuple[list[dict], list[dict]]:
    """
    Load ward_budget.csv, filter for the given ward and category,
    separate null actual_spend rows and report them before returning.

    Returns: (valid_rows, null_rows)
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {file_path}")

    if not rows:
        raise ValueError("The CSV file is empty.")

    actual_columns = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - actual_columns
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Filter to the specified ward and category
    filtered = [
        r for r in rows
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'. "
            "Check spelling — values are case-sensitive."
        )

    # Separate nulls from valid rows
    null_rows = []
    valid_rows = []
    for r in filtered:
        spend = r.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_rows.append({
                "period":   r["period"],
                "ward":     r["ward"],
                "category": r["category"],
                "notes":    r.get("notes", ""),
            })
        else:
            try:
                r["actual_spend_float"] = float(spend)
                valid_rows.append(r)
            except ValueError:
                null_rows.append({
                    "period":   r["period"],
                    "ward":     r["ward"],
                    "category": r["category"],
                    "notes":    f"Invalid actual_spend value: '{spend}'",
                })

    # --- Enforcement: null report before computation ---
    print(f"\nNULL REPORT — Before computation")
    print(f"  Ward    : {ward}")
    print(f"  Category: {category}")
    print(f"  Null rows found: {len(null_rows)}")
    if null_rows:
        for n in null_rows:
            print(f"    [{n['period']}] {n['ward']} / {n['category']} — {n['notes']}")
    print()

    if not valid_rows:
        raise ValueError(
            f"All rows for ward='{ward}', category='{category}' have null actual_spend. "
            "No computation possible."
        )

    # Sort by period ascending
    valid_rows.sort(key=lambda r: r["period"])
    return valid_rows, null_rows


def compute_growth(
    valid_rows: list[dict],
    growth_type: str,
    ward: str,
    category: str,
) -> list[dict]:
    """
    Compute MoM or YoY growth for each period in valid_rows.
    Every output row includes the formula used.
    """
    growth_type_upper = growth_type.upper()
    if growth_type_upper not in ("MOM", "YOY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY'. Received: '{growth_type}'. "
            "Provide --growth-type explicitly."
        )

    # Build period → spend map for YoY lookups
    spend_by_period = {r["period"]: r["actual_spend_float"] for r in valid_rows}

    results = []
    for i, row in enumerate(valid_rows):
        period = row["period"]
        current_spend = row["actual_spend_float"]
        growth_pct: Optional[float] = None
        formula: str = ""
        note: str = ""

        if growth_type_upper == "MOM":
            if i == 0:
                note = "First period — no prior month available"
                formula = "N/A"
            else:
                prev_spend = valid_rows[i - 1]["actual_spend_float"]
                prev_period = valid_rows[i - 1]["period"]
                if prev_spend == 0:
                    note = "Division by zero — prior period actual_spend is 0"
                    formula = f"({current_spend} - {prev_spend}) / {prev_spend} × 100 = undefined"
                else:
                    growth_pct = (current_spend - prev_spend) / prev_spend * 100
                    formula = (
                        f"MoM = ({current_spend} - {prev_spend}) / {prev_spend} × 100"
                        f" = {growth_pct:.1f}%  [vs {prev_period}]"
                    )

        elif growth_type_upper == "YOY":
            # Find same month one year prior
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
            if prior_period not in spend_by_period:
                note = f"No data for prior year period {prior_period}"
                formula = "N/A"
            else:
                prior_spend = spend_by_period[prior_period]
                if prior_spend == 0:
                    note = "Division by zero — prior year actual_spend is 0"
                    formula = f"({current_spend} - {prior_spend}) / {prior_spend} × 100 = undefined"
                else:
                    growth_pct = (current_spend - prior_spend) / prior_spend * 100
                    formula = (
                        f"YoY = ({current_spend} - {prior_spend}) / {prior_spend} × 100"
                        f" = {growth_pct:.1f}%  [vs {prior_period}]"
                    )

        results.append({
            "period":       period,
            "ward":         ward,
            "category":     category,
            "actual_spend": current_spend,
            "growth_pct":   f"{growth_pct:.1f}%" if growth_pct is not None else "N/A",
            "formula":      formula,
            "note":         note,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name (e.g. 'Ward 1 - Kasba')")
    parser.add_argument("--category",    required=True,  help="Exact category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path for output CSV")
    args = parser.parse_args()

    # --- Enforcement: refuse if growth-type not provided ---
    if not args.growth_type:
        print(
            "[REFUSED] Growth type not specified. "
            "Please provide --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    growth_type = args.growth_type.upper()

    # Step 1: Load and report nulls
    print(f"Loading dataset: {args.input}")
    valid_rows, null_rows = load_dataset(args.input, args.ward, args.category)
    print(f"Valid rows for computation: {len(valid_rows)}")

    # Step 2: Compute growth
    results = compute_growth(valid_rows, growth_type, args.ward, args.category)

    # Step 3: Write output
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "note"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")
    print(f"  Rows computed: {len(results)}")
    print(f"  Null rows (excluded): {len(null_rows)}")


if __name__ == "__main__":
    main()
