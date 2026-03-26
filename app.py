"""
UC-0C: The Number That Looks Right
BudgetGuard — Ward Budget Growth Analyser

Reads ward_budget.csv, computes per-ward per-category year-over-year
budget growth, flags anomalies, and writes growth_output.csv.

CRAFT loop commit trail:
  v1 → fixed silent ward aggregation
  v2 → fixed missing-year zero imputation
  v3 → fixed growth on aggregated rows
  v4 → added mandatory scope column

Usage:
    python app.py [--input PATH] [--output PATH]

Defaults:
    --input  ../../data/budget/ward_budget.csv
    --output growth_output.csv
"""

import csv
import sys
import argparse
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HIGH_GROWTH_THRESHOLD = 200.0   # %
LARGE_CUT_THRESHOLD   = -50.0   # %


# ---------------------------------------------------------------------------
# Step 1 — Load CSV
# ---------------------------------------------------------------------------
def load_budget(path: Path) -> list[dict]:
    """Load ward_budget.csv into a list of row dicts."""
    if not path.exists():
        print(f"[ERROR] Input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"ward", "category", "year", "budget"}
        missing  = required - set(reader.fieldnames or [])
        if missing:
            print(f"[ERROR] CSV is missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

        for i, row in enumerate(reader, start=2):          # row 1 = header
            try:
                row["year"]   = int(row["year"].strip())
                row["budget"] = float(row["budget"].strip().replace(",", "").replace("₹", "").replace("L", ""))
                row["ward"]   = row["ward"].strip()
                row["category"] = row["category"].strip()
                rows.append(row)
            except ValueError as e:
                print(f"[WARN] Skipping row {i} — parse error: {e}")

    if not rows:
        print("[ERROR] No valid rows loaded.", file=sys.stderr)
        sys.exit(1)

    return rows


# ---------------------------------------------------------------------------
# Step 2 — Pivot: (ward, category) → {year: budget}
# ---------------------------------------------------------------------------
def pivot_data(rows: list[dict]) -> dict:
    """
    Returns:
        data[(ward, category)][year] = budget_value
    Scope is strictly per-ward per-category — never collapsed.
    """
    data = defaultdict(dict)
    for row in rows:
        key = (row["ward"], row["category"])
        year = row["year"]
        if year in data[key]:
            print(f"[WARN] Duplicate entry for ward='{row['ward']}' "
                  f"category='{row['category']}' year={year} — keeping first occurrence.")
        else:
            data[key][year] = row["budget"]
    return data


# ---------------------------------------------------------------------------
# Step 3 — Compute growth (per-ward, per-category, consecutive years only)
# ---------------------------------------------------------------------------
def compute_growth(data: dict) -> list[dict]:
    """
    For each (ward, category), compute growth between consecutive years.
    Never aggregates across wards or categories.
    Flags missing data, zero-base, and outliers.
    """
    results = []

    for (ward, category), year_map in data.items():
        years = sorted(year_map.keys())

        for i in range(len(years) - 1):
            y_from = years[i]
            y_to   = years[i + 1]

            b_from = year_map.get(y_from)
            b_to   = year_map.get(y_to)

            flags = []

            # --- Guard: missing data (should not happen after pivot, but defensive) ---
            if b_from is None or b_to is None:
                flags.append("DATA_MISSING")
                growth_pct = None
            elif b_from == 0:
                flags.append("ZERO_BASE")
                growth_pct = None          # undefined, not zero
            else:
                growth_pct = round(((b_to - b_from) / b_from) * 100, 2)

                # Outlier detection
                if growth_pct > HIGH_GROWTH_THRESHOLD:
                    flags.append("HIGH_GROWTH_OUTLIER")
                elif growth_pct < LARGE_CUT_THRESHOLD:
                    flags.append("LARGE_CUT_OUTLIER")

            if not flags:
                flags.append("OK")

            results.append({
                "ward":        ward,
                "category":    category,
                "year_from":   y_from,
                "year_to":     y_to,
                "budget_from": b_from,
                "budget_to":   b_to,
                "growth_pct":  growth_pct,
                "scope":       "per_ward_per_category",   # MANDATORY — never omit
                "flag":        "|".join(flags),
            })

    return results


# ---------------------------------------------------------------------------
# Step 4 — Write growth_output.csv
# ---------------------------------------------------------------------------
FIELDNAMES = [
    "ward", "category", "year_from", "year_to",
    "budget_from", "budget_to", "growth_pct", "scope", "flag",
]

def write_output(results: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)


# ---------------------------------------------------------------------------
# Step 5 — Summary reporter (stdout)
# ---------------------------------------------------------------------------
def print_summary(results: list[dict], output_path: Path) -> None:
    wards      = sorted({r["ward"] for r in results})
    categories = sorted({r["category"] for r in results})
    years      = sorted({r["year_from"] for r in results} | {r["year_to"] for r in results})

    flagged     = [r for r in results if r["flag"] != "OK"]
    data_miss   = sum(1 for r in results if "DATA_MISSING"        in r["flag"])
    zero_base   = sum(1 for r in results if "ZERO_BASE"           in r["flag"])
    outliers    = sum(1 for r in results if "HIGH_GROWTH_OUTLIER" in r["flag"]
                                         or "LARGE_CUT_OUTLIER"  in r["flag"])

    valid = [r for r in results if r["growth_pct"] is not None]
    top_growth = sorted(valid, key=lambda r: r["growth_pct"], reverse=True)[:3]
    top_cuts   = sorted(valid, key=lambda r: r["growth_pct"])[:3]

    sep = "=" * 62
    print(f"\n{sep}")
    print("  BudgetGuard — Ward Budget Growth Report")
    print(sep)
    print(f"  Wards analysed    : {len(wards)}")
    print(f"  Categories        : {', '.join(categories)}")
    print(f"  Year range        : {min(years)} → {max(years)}")
    print(f"  Rows computed     : {len(results)}")
    print(f"  Flagged rows      : {len(flagged)} "
          f"(DATA_MISSING: {data_miss} | ZERO_BASE: {zero_base} | OUTLIERS: {outliers})")
    print(sep)

    if top_growth:
        print("  Top 3 fastest-growing (ward | category):")
        for i, r in enumerate(top_growth, 1):
            print(f"    {i}. {r['ward']} | {r['category']} : +{r['growth_pct']}%")

    if top_cuts:
        print("  Top 3 largest budget cuts:")
        for i, r in enumerate(top_cuts, 1):
            sign = "" if r["growth_pct"] >= 0 else ""
            print(f"    {i}. {r['ward']} | {r['category']} : {r['growth_pct']}%")

    print(sep)
    print(f"  Output saved → {output_path.resolve()}")
    print(f"{sep}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UC-0C BudgetGuard — Ward Budget Growth Analyser")
    parser.add_argument(
        "--input", "-i",
        default=str(Path(__file__).parent.parent / "data" / "budget" / "ward_budget.csv"),
        help="Path to ward_budget.csv (default: ../../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--output", "-o",
        default="growth_output.csv",
        help="Output CSV path (default: growth_output.csv)",
    )
    return parser.parse_args()


def main() -> None:
    args   = parse_args()
    inp    = Path(args.input)
    out    = Path(args.output)

    print(f"[INFO] Loading budget data from: {inp}")
    rows   = load_budget(inp)
    print(f"[INFO] Loaded {len(rows)} records.")

    data    = pivot_data(rows)
    print(f"[INFO] Unique (ward, category) pairs: {len(data)}")

    results = compute_growth(data)
    print(f"[INFO] Growth rows computed: {len(results)}")

    write_output(results, out)
    print_summary(results, out)


if __name__ == "__main__":
    main()
