"""
UC-0C app.py — Per-ward, per-category growth calculator.
See README.md for run command, reference values, and enforcement rules.
"""
import argparse
import csv
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ["MoM", "YoY"]


def load_dataset(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("file is empty")
            missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(
                    f"input is missing required column(s): {', '.join(missing)}"
                )
            rows = [row for row in reader if any((row.get(c) or "").strip() for c in EXPECTED_COLUMNS)]
    except FileNotFoundError:
        sys.exit(f"REFUSED: input file not found: {path}")
    except (OSError, ValueError) as e:
        sys.exit(f"REFUSED: could not read input: {e}")

    for row in rows:
        actual = (row.get("actual_spend") or "").strip()
        row["_actual"] = float(actual) if actual else None

    null_rows = [r for r in rows if r["_actual"] is None]
    print(f"Null actual_spend rows found: {len(null_rows)}")
    for r in null_rows:
        reason = (r.get("notes") or "").strip() or "(no reason given)"
        print(f"  {r['period']} | {r['ward']} | {r['category']} | reason: {reason}")

    return rows


def compute_growth(rows, ward, category, growth_type):
    wards = {r["ward"] for r in rows}
    categories = {r["category"] for r in rows}
    if ward not in wards:
        sys.exit(f"REFUSED: ward not found in dataset: {ward}")
    if category not in categories:
        sys.exit(f"REFUSED: category not found in dataset: {category}")

    scoped = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    if not scoped:
        sys.exit(f"REFUSED: no rows for {ward} / {category} in dataset")

    if growth_type not in VALID_GROWTH_TYPES:
        sys.exit(
            f"REFUSED: --growth-type must be MoM or YoY, got '{growth_type}' — ask, never guess."
        )

    formula = "MoM = (current − prev) / prev" if growth_type == "MoM" else \
              "YoY = (current − same_month_prev_year) / same_month_prev_year"

    out = []
    for i, r in enumerate(scoped):
        actual = r["_actual"]
        note = (r.get("notes") or "").strip()
        if actual is None:
            growth = "FLAGGED — not computed (null actual_spend)"
            reason = note or "(no reason given)"
            formula_shown = f"{formula}; row flagged: {reason}"
        else:
            prev_actual = scoped[i - 1]["_actual"] if growth_type == "MoM" and i > 0 else None
            if growth_type == "YoY":
                prev_actual = next(
                    (p["_actual"] for p in rows
                     if p["ward"] == ward and p["category"] == category
                     and p["period"] == str(int(r["period"][:4]) - 1) + r["period"][4:]),
                    None,
                )
                if prev_actual is None:
                    growth = "N/A — no prior-year data in dataset"
                    formula_shown = formula
                elif prev_actual == 0:
                    growth = "N/A — previous period is zero"
                    formula_shown = formula
                else:
                    growth = f"{(actual - prev_actual) / prev_actual * 100:+.1f}%"
                    formula_shown = formula
            elif prev_actual is None:
                growth = "N/A — no previous period"
                formula_shown = formula
            elif prev_actual == 0:
                growth = "N/A — previous period is zero"
                formula_shown = formula
            else:
                growth = f"{(actual - prev_actual) / prev_actual * 100:+.1f}%"
                formula_shown = formula
        out.append({
            "period": r["period"],
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual:.1f}" if actual is not None else "NULL",
            "growth": growth,
            "formula": formula_shown,
        })
    return out


def main():
    parser = argparse.ArgumentParser(description="Compute growth for one ward + one category.")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv")
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", default="growth_output.csv")
    args = parser.parse_args()

    rows = load_dataset(args.input)

    if not args.growth_type:
        sys.exit("REFUSED: --growth-type is required (MoM or YoY) — ask, never guess.")

    table = compute_growth(rows, args.ward, args.category, args.growth_type)

    print(f"\nGrowth table: {args.ward} / {args.category} ({args.growth_type})")
    for row in table:
        print(f"  {row['period']} | actual={row['actual_spend']} | growth={row['growth']} | {row['formula']}")

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(table)
    print(f"\nWrote {len(table)} rows to {args.output}")


if __name__ == "__main__":
    main()
