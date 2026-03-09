"""
UC-0C — Number That Looks Right
Author: Gaddam Siddharth | City: Hyderabad
CRAFT loop: compute per-ward per-category budget growth — no silent aggregation
"""

import csv
import os

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE  = os.path.join(os.path.dirname(__file__), "../data/budget/ward_budget.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../growth_output.csv")


# ── Skills ────────────────────────────────────────────────────────────────────

def read_budget_csv(filepath: str) -> list:
    """Read budget CSV and return list of row dicts."""
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def compute_growth(previous_year: float, current_year: float) -> tuple:
    """
    Compute growth % for a single ward-category row.
    NEVER call this on aggregated totals.
    """
    if previous_year == 0:
        return ("DIV_ZERO", "DIV_ZERO")

    growth_pct = ((current_year - previous_year) / previous_year) * 100
    growth_pct = round(growth_pct, 2)

    if growth_pct > 0:
        direction = "UP"
    elif growth_pct < 0:
        direction = "DOWN"
    else:
        direction = "FLAT"

    return (str(growth_pct), direction)


def write_growth_csv(filepath: str, results: list):
    """Write growth results to output CSV."""
    fieldnames = ["ward", "category", "previous_year", "current_year", "growth_pct", "growth_direction"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Reading budget data: {INPUT_FILE}")

    if not os.path.exists(INPUT_FILE):
        print("  ⚠  File not found — creating sample budget data for testing")
        os.makedirs(os.path.dirname(INPUT_FILE), exist_ok=True)
        sample_rows = [
            ["ward", "category", "previous_year", "current_year"],
            ["Ward-1", "Roads",       "500000",  "575000"],
            ["Ward-1", "Water",       "300000",  "290000"],
            ["Ward-1", "Sanitation",  "200000",  "200000"],
            ["Ward-2", "Roads",       "450000",  "520000"],
            ["Ward-2", "Water",       "350000",  "400000"],
            ["Ward-2", "Electricity", "150000",  "180000"],
            ["Ward-3", "Roads",       "0",       "100000"],
            ["Ward-3", "Sanitation",  "180000",  "160000"],
        ]
        with open(INPUT_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(sample_rows)

    rows = read_budget_csv(INPUT_FILE)
    print(f"  → {len(rows)} rows loaded")

    results = []
    for row in rows:
        # ── Per-row computation — no aggregation ──────────────────────────────
        try:
            prev = float(row.get("previous_year", 0))
            curr = float(row.get("current_year", 0))
        except ValueError:
            prev, curr = 0.0, 0.0

        growth_pct, direction = compute_growth(prev, curr)

        results.append({
            "ward":             row.get("ward", ""),
            "category":         row.get("category", ""),
            "previous_year":    row.get("previous_year", ""),
            "current_year":     row.get("current_year", ""),
            "growth_pct":       growth_pct,
            "growth_direction": direction,
        })

    write_growth_csv(OUTPUT_FILE, results)
    print(f"\nGrowth output written to: {OUTPUT_FILE}")

    # Summary
    up   = sum(1 for r in results if r["growth_direction"] == "UP")
    down = sum(1 for r in results if r["growth_direction"] == "DOWN")
    flat = sum(1 for r in results if r["growth_direction"] == "FLAT")
    div0 = sum(1 for r in results if r["growth_direction"] == "DIV_ZERO")
    print(f"\n── Growth Summary ──")
    print(f"  UP       : {up}")
    print(f"  DOWN     : {down}")
    print(f"  FLAT     : {flat}")
    print(f"  DIV_ZERO : {div0}")


if __name__ == "__main__":
    main()
