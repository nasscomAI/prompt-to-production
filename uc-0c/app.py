"""
UC-0C — Number That Looks Right
Budget growth calculator built from agents.md and skills.md specifications.
"""
import argparse
import csv
import re
import sys

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Required columns
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]

OUTPUT_FIELDS = ["period", "ward", "category", "actual_spend",
                 "previous_spend", "formula", "growth_rate", "flag"]


def _normalize(text: str) -> str:
    """Normalize text for fuzzy matching — strips all non-alphanumeric chars."""
    # Remove everything except letters, digits, and spaces
    return re.sub(r"[^a-zA-Z0-9 ]", "", text).strip().lower()


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> list[dict]:
    """
    Read ward_budget.csv, validate required columns, and report null
    actual_spend rows before returning the data.
    """
    rows = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(file_path, newline="", encoding=encoding) as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    continue

                missing_cols = [c for c in REQUIRED_COLUMNS
                                if c not in reader.fieldnames]
                if missing_cols:
                    print(f"Error: Missing required columns: {missing_cols}",
                          file=sys.stderr)
                    sys.exit(1)

                rows = list(reader)
                break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if rows is None:
        print(f"Error: Could not read {file_path} with any encoding.",
              file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Error: Dataset is empty — no data rows found.", file=sys.stderr)
        sys.exit(1)

    # --- Null report (enforcement: flag every null before computing) ---
    null_rows = [r for r in rows if not r.get("actual_spend", "").strip()]
    print(f"Loaded {len(rows)} rows from {file_path}")
    print(f"Null actual_spend rows found: {len(null_rows)}")
    if null_rows:
        print("\n--- NULL REPORT ---")
        for r in null_rows:
            note = r.get("notes", "").strip() or "No reason provided"
            print(f"  {r['period']} | {r['ward']} | {r['category']} | "
                  f"Reason: {note}")
        print("-------------------\n")

    return rows


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list[dict], ward: str, category: str,
                   growth_type: str) -> list[dict]:
    """
    Filter data to a specific ward and category, then compute per-period
    MoM growth rates with the formula shown alongside each result.

    Enforcement:
      - Never aggregate across wards or categories
      - Flag null rows — do not compute growth from incomplete data
      - Show formula in every output row
    """
    # Validate ward and category exist (normalized matching for dash variants)
    available_wards = sorted(set(r["ward"] for r in rows))
    available_cats = sorted(set(r["category"] for r in rows))

    ward_match = next((w for w in available_wards
                       if _normalize(w) == _normalize(ward)), None)
    if not ward_match:
        print(f"Error: Ward '{ward}' not found.", file=sys.stderr)
        print(f"Available wards: {available_wards}", file=sys.stderr)
        sys.exit(1)
    ward = ward_match

    cat_match = next((c for c in available_cats
                      if _normalize(c) == _normalize(category)), None)
    if not cat_match:
        print(f"Error: Category '{category}' not found.", file=sys.stderr)
        print(f"Available categories: {available_cats}", file=sys.stderr)
        sys.exit(1)
    category = cat_match

    # Filter to the single ward + category
    filtered = [r for r in rows
                if r["ward"] == ward and r["category"] == category]

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(f"Error: No data for ward='{ward}', category='{category}'.",
              file=sys.stderr)
        sys.exit(1)

    # Compute MoM growth
    results: list[dict] = []
    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row.get("actual_spend", "").strip()
        note = row.get("notes", "").strip()
        is_null = not spend_str

        if is_null:
            # Current period is null
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_spend": "",
                "formula": "N/A",
                "growth_rate": "N/A",
                "flag": f"NULL — {note or 'No reason provided'}",
            })
            continue

        actual = float(spend_str)

        if i == 0:
            # First period — no previous to compare
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual}",
                "previous_spend": "N/A",
                "formula": "N/A (first period)",
                "growth_rate": "N/A",
                "flag": "",
            })
            continue

        # Check if previous period is null
        prev_row = filtered[i - 1]
        prev_str = prev_row.get("actual_spend", "").strip()
        prev_is_null = not prev_str

        if prev_is_null:
            prev_note = prev_row.get("notes", "").strip()
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual}",
                "previous_spend": "NULL",
                "formula": "N/A",
                "growth_rate": "N/A",
                "flag": f"Previous period ({prev_row['period']}) is NULL — "
                        f"{prev_note or 'No reason provided'}",
            })
            continue

        # Both current and previous are valid — compute MoM
        previous = float(prev_str)
        if previous == 0:
            formula = f"({actual} - 0) / 0 * 100"
            growth = "N/A"
            flag = "Division by zero — previous spend is 0"
        else:
            growth_val = ((actual - previous) / previous) * 100
            formula = f"({actual} - {previous}) / {previous} * 100"
            growth = f"{growth_val:+.1f}%"
            flag = ""

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual}",
            "previous_spend": f"{previous}",
            "formula": formula,
            "growth_rate": growth,
            "flag": flag,
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Calculator (Number That Looks Right)"
    )
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Ward name to filter (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True,
                        help="Category to filter (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, default=None,
                        help="Growth type: MoM (required — will refuse if missing)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified
    if not args.growth_type:
        print("Error: --growth-type is required. Please specify 'MoM'.",
              file=sys.stderr)
        print("REFUSED: Will not silently assume a growth type.",
              file=sys.stderr)
        sys.exit(1)

    if args.growth_type != "MoM":
        print(f"Error: Unsupported growth type '{args.growth_type}'. "
              f"Currently supported: MoM", file=sys.stderr)
        sys.exit(1)

    # Step 1: Load and validate dataset
    rows = load_dataset(args.input)

    # Step 2: Compute growth for single ward + category
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Step 3: Write output
    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        print(f"Error writing output: {exc}", file=sys.stderr)
        sys.exit(1)

    # Step 4: Report
    null_count = sum(1 for r in results if "NULL" in r.get("flag", ""))
    computed = sum(1 for r in results
                   if r["growth_rate"] not in ("N/A", ""))
    print(f"Computed {computed} MoM growth rates for "
          f"{args.ward} / {args.category}")
    if null_count:
        print(f"Flagged {null_count} period(s) affected by null data")
    print(f"Done. Output written to {args.output}")


if __name__ == "__main__":
    main()
