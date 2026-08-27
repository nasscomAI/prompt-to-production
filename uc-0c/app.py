"""
UC-0C app.py — Growth Calculator
Built per agents.md (per-ward per-category scope only, null rows flagged not
computed, formula shown, growth-type never defaulted) and skills.md
(load_dataset, compute_growth).
"""
import argparse
import csv

EXPECTED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(input_path: str) -> dict:
    """
    Reads ward_budget.csv, validates columns, reports null actual_spend rows
    before any computation.
    Returns: dict with keys `rows` and `null_rows`.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing = EXPECTED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"ward_budget.csv is missing expected column(s): {sorted(missing)}")

        rows = []
        null_rows = []
        for row in reader:
            raw_spend = (row.get("actual_spend") or "").strip()
            row["actual_spend"] = float(raw_spend) if raw_spend else None
            row["budgeted_amount"] = float(row["budgeted_amount"])
            rows.append(row)
            if row["actual_spend"] is None:
                null_rows.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"],
                })

    return {"rows": rows, "null_rows": null_rows}


def _prior_period(period: str, growth_type: str) -> str:
    year, month = (int(p) for p in period.split("-"))
    if growth_type == "MoM":
        return f"{year}-{month - 1:02d}" if month > 1 else f"{year - 1}-12"
    return f"{year - 1}-{month:02d}"  # YoY


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes per-period growth for one ward + category using the specified
    growth type, showing the formula used for every row.
    Returns: list of dicts with keys period, actual_spend, growth_pct, formula.
    """
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"--growth-type must be specified as MoM or YoY — refusing to default silently (got: {growth_type!r})"
        )

    scoped = {r["period"]: r for r in rows if r["ward"] == ward and r["category"] == category}
    if not scoped:
        raise ValueError(f"No rows found for ward={ward!r} category={category!r} — refusing to guess or aggregate.")

    results = []
    for period in sorted(scoped):
        row = scoped[period]
        actual = row["actual_spend"]

        if actual is None:
            results.append({
                "period": period,
                "actual_spend": None,
                "growth_pct": "flagged",
                "formula": f"not computed — null actual_spend ({row['notes']})",
            })
            continue

        prior_period = _prior_period(period, growth_type)
        prior_row = scoped.get(prior_period)

        if prior_row is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth_pct": "flagged",
                "formula": f"not computed — no {prior_period} data for {growth_type} comparison",
            })
            continue

        prior_actual = prior_row["actual_spend"]
        if prior_actual is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth_pct": "flagged",
                "formula": f"not computed — {prior_period} actual_spend is null ({prior_row['notes']})",
            })
            continue

        growth_pct = round((actual - prior_actual) / prior_actual * 100, 1)
        results.append({
            "period": period,
            "actual_spend": actual,
            "growth_pct": growth_pct,
            "formula": f"({actual} - {prior_actual}) / {prior_actual} = {growth_pct}% ({growth_type} vs {prior_period})",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name, exact match (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name, exact match")
    parser.add_argument("--growth-type", required=True, choices=sorted(VALID_GROWTH_TYPES),
                         help="MoM or YoY — must be specified explicitly")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    if dataset["null_rows"]:
        print(f"NOTICE: {len(dataset['null_rows'])} null actual_spend rows in dataset (flagged, not computed):")
        for nr in dataset["null_rows"]:
            print(f"  {nr['period']} · {nr['ward']} · {nr['category']} — {nr['notes']}")

    results = compute_growth(dataset["rows"], args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth_pct", "formula"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth table for {args.ward} / {args.category} written to {args.output}")


if __name__ == "__main__":
    main()
