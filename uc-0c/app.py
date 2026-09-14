"""
UC-0C — Number That Looks Right
Deterministic, stdlib-only. See agents.md / skills.md for the enforcement
rules this file implements.
"""
import argparse
import csv

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str) -> list:
    with open(input_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"ward_budget.csv is missing required column(s): {missing}")
        rows = list(reader)

    nulls = [r for r in rows if not r["actual_spend"].strip()]
    print(f"load_dataset: {len(rows)} rows loaded, {len(nulls)} null actual_spend row(s):")
    for r in nulls:
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes'] or '(no reason given)'}")

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"--growth-type must be MoM or YoY, got: {growth_type!r}")

    scoped = sorted(
        [r for r in rows if r["ward"] == ward and r["category"] == category],
        key=lambda r: r["period"],
    )
    if not scoped:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}. Refusing to emit a fabricated table.")

    by_period = {r["period"]: r for r in scoped}
    result = []

    for i, row in enumerate(scoped):
        period = row["period"]
        raw_spend = row["actual_spend"].strip()

        if not raw_spend:
            result.append({
                "period": period, "actual_spend": "", "growth_pct": "",
                "formula": "n/a", "flag": f"NULL actual_spend — {row['notes'] or 'no reason given'}",
            })
            continue

        actual_spend = float(raw_spend)

        if growth_type == "MoM":
            prior = scoped[i - 1] if i > 0 else None
        else:  # YoY
            year, month = period.split("-")
            prior_period = f"{int(year) - 1}-{month}"
            prior = by_period.get(prior_period)

        if prior is None:
            reason = "no prior period in this ward/category's data" if growth_type == "MoM" else "no prior-year data available for this period"
            result.append({
                "period": period, "actual_spend": actual_spend, "growth_pct": "",
                "formula": "n/a", "flag": reason,
            })
            continue

        prior_raw = prior["actual_spend"].strip()
        if not prior_raw:
            result.append({
                "period": period, "actual_spend": actual_spend, "growth_pct": "",
                "formula": "n/a", "flag": f"prior period ({prior['period']}) is NULL — cannot compute growth",
            })
            continue

        prior_spend = float(prior_raw)
        growth_pct = (actual_spend - prior_spend) / prior_spend * 100
        result.append({
            "period": period,
            "actual_spend": actual_spend,
            "growth_pct": round(growth_pct, 1),
            "formula": f"({actual_spend} - {prior_spend}) / {prior_spend} * 100  [vs {prior['period']}]",
            "flag": "",
        })

    return result


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="MoM or YoY — no default, must be explicit")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=["period", "actual_spend", "growth_pct", "formula", "flag"])
        writer.writeheader()
        writer.writerows(growth_rows)

    print(f"Done. Growth table written to {args.output}")


if __name__ == "__main__":
    main()
