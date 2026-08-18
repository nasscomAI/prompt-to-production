"""
UC-0C — Number That Looks Right

Computes per-period growth for exactly one ward + one category from
ward_budget.csv. Refuses to aggregate across wards/categories, flags null
actual_spend rows instead of computing on them, and shows the formula used
on every output row.

Usage:
    python app.py --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" \
        --category "Roads & Pothole Repair" \
        --growth-type MoM \
        --output growth_output.csv
"""

import argparse
import csv

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "growth_pct",
    "formula",
    "flag",
]

WILDCARDS = {"any", "all", "*", "n/a", ""}


def load_dataset(input_path: str):
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {input_path}")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Input CSV missing required columns: {', '.join(missing)}"
            )
        rows = list(reader)

    nulls = []
    for i, row in enumerate(rows):
        if (row.get("actual_spend") or "").strip() == "":
            nulls.append(
                {
                    "row": i + 2,
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": (row.get("notes") or "").strip(),
                }
            )

    print(f"Loaded {len(rows)} rows from {input_path}.")
    if nulls:
        print(
            f"WARNING: {len(nulls)} rows have null actual_spend - these are "
            "flagged, never computed on:"
        )
        for n in nulls:
            reason = n["reason"] or "(none given)"
            print(
                f"  row {n['row']}: {n['period']} | {n['ward']} | "
                f"{n['category']} | reason: {reason}"
            )
    else:
        print("No null actual_spend rows found.")
    return rows, nulls


def refuse_wildcards(ward: str, category: str) -> None:
    if ward.strip().lower() in WILDCARDS or category.strip().lower() in WILDCARDS:
        raise SystemExit(
            "REFUSED: aggregating across wards/categories is not permitted. "
            "Specify exactly one ward and one category."
        )


def compute_growth(rows, ward: str, category: str, growth_type: str):
    selected = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    if not selected:
        raise SystemExit(
            f"REFUSED: no rows found for ward='{ward}', category='{category}'. "
            "Cannot aggregate across wards or categories."
        )
    selected.sort(key=lambda r: r["period"])

    if growth_type == "MoM":
        label = "MoM = (actual_spend[current] - actual_spend[previous]) / actual_spend[previous] * 100"
    else:
        label = "YoY = (actual_spend[current] - actual_spend[same month prev year]) / actual_spend[same month prev year] * 100"

    out = []
    for idx, r in enumerate(selected):
        spend_raw = (r.get("actual_spend") or "").strip()
        budget = float(r["budgeted_amount"])
        spend = float(spend_raw) if spend_raw else None
        growth = ""
        formula = ""
        flag = ""

        if spend is None:
            flag = "FLAGGED - actual_spend is null"
            note = (r.get("notes") or "").strip() or "no reason given"
            formula = f"N/A - {flag}; reason from notes: '{note}'"
        else:
            prev = None
            if idx > 0:
                prev_raw = (selected[idx - 1].get("actual_spend") or "").strip()
                prev = float(prev_raw) if prev_raw else None
            if prev is None:
                growth = "N/A"
                formula = f"{label} - no prior period with data for {r['period']}"
            else:
                value = (spend - prev) / prev * 100
                growth = f"{value:+.1f}%"
                formula = (
                    f"({spend:.1f} - {prev:.1f}) / {prev:.1f} * 100 = {growth}"
                )

        out.append(
            {
                "period": r["period"],
                "ward": ward,
                "category": category,
                "budgeted_amount": f"{budget:.1f}",
                "actual_spend": spend_raw if spend_raw else "NULL",
                "growth_pct": growth,
                "formula": formula,
                "flag": flag,
            }
        )
    return out


def write_output(output_path: str, rows) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward")
    parser.add_argument("--category", required=True, help="Exactly one category")
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
        help="Required - never guessed: MoM or YoY",
    )
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    rows, _nulls = load_dataset(args.input)
    refuse_wildcards(args.ward, args.category)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, results)


if __name__ == "__main__":
    main()
