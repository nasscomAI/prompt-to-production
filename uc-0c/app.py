"""
UC-0C app.py — Ward/category budget growth calculator.
Built per agents.md (role/intent/context/enforcement) and skills.md
(load_dataset, compute_growth).
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str):
    """
    Reads ward_budget.csv, validates columns, and reports every null
    actual_spend row before returning any data.
    Returns: (rows, null_report)
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"ward_budget.csv is missing required column(s): {missing}")
        rows = list(reader)

    null_report = [
        {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "reason": row["notes"] or "No reason given in notes column.",
        }
        for row in rows
        if not row["actual_spend"].strip()
    ]

    return rows, null_report


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM or YoY growth in actual_spend for exactly one ward and
    one category. Returns a per-period table with the formula shown and
    every null-dependent period reported as not computed.
    """
    if not ward or not category:
        raise ValueError("ward and category are both required — refusing to aggregate across wards/categories.")
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("growth_type must be exactly 'MoM' or 'YoY' — refusing to guess.")

    scoped = sorted(
        (row for row in rows if row["ward"] == ward and row["category"] == category),
        key=lambda r: r["period"],
    )
    if not scoped:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}.")

    lag = 1 if growth_type == "MoM" else 12
    results = []
    for i, row in enumerate(scoped):
        period = row["period"]
        actual_raw = row["actual_spend"].strip()

        if not actual_raw:
            results.append({
                "period": period, "actual_spend": "", "growth_pct": "not computed",
                "formula": "n/a", "note": f"actual_spend is null: {row['notes'] or 'no reason given'}",
            })
            continue

        actual = float(actual_raw)
        prior_index = i - lag
        if prior_index < 0:
            results.append({
                "period": period, "actual_spend": actual, "growth_pct": "not computed",
                "formula": "n/a", "note": f"no {growth_type} comparison period available in dataset",
            })
            continue

        prior_raw = scoped[prior_index]["actual_spend"].strip()
        if not prior_raw:
            results.append({
                "period": period, "actual_spend": actual, "growth_pct": "not computed",
                "formula": "n/a",
                "note": f"comparison period {scoped[prior_index]['period']} actual_spend is null: "
                        f"{scoped[prior_index]['notes'] or 'no reason given'}",
            })
            continue

        prior = float(prior_raw)
        growth = (actual - prior) / prior
        results.append({
            "period": period,
            "actual_spend": actual,
            "growth_pct": f"{growth * 100:+.1f}%",
            "formula": f"({actual}-{prior})/{prior}",
            "note": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", help="Exact category name, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows. {len(null_report)} rows have a null actual_spend:")
    for entry in null_report:
        print(f"  - {entry['period']} · {entry['ward']} · {entry['category']}: {entry['reason']}")

    if not args.ward or not args.category:
        sys.exit("Refusing to proceed: --ward and --category are both required. "
                  "This tool never aggregates across wards or categories.")
    if not args.growth_type:
        sys.exit("Refusing to proceed: --growth-type must be MoM or YoY. This tool never guesses.")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth_pct", "formula", "note"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} periods written to {args.output}")


if __name__ == "__main__":
    main()
