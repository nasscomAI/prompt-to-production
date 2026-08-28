"""
UC-0C — Number That Looks Right
RICE-enforced budget growth calculator. Rules from agents.md, structure from skills.md.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str) -> dict:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        rows = [dict(r) for r in reader]

    if not rows:
        raise ValueError(f"No rows found in {input_path}")

    nulls = [
        {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "notes": (r.get("notes") or "").strip() or "no reason recorded",
        }
        for r in rows
        if not (r.get("actual_spend") or "").strip()
    ]
    return {"rows": rows, "nulls": nulls}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    if growth_type != "MoM":
        raise SystemExit(
            f"REFUSED: growth type '{growth_type}' is not supported. "
            "The dataset covers a single year (2024); no prior-year data exists "
            "for YoY. Specify --growth-type MoM or ask for a supported type. "
            "Never guessing."
        )

    filtered = [
        r for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise ValueError(
            f"REFUSED: no data found for ward '{ward}' + category '{category}'. "
            "Not guessing with a different scope."
        )

    filtered.sort(key=lambda r: r["period"])
    null_periods = {n["period"]: n for n in dataset["nulls"]}

    out = []
    for i, row in enumerate(filtered):
        actual = row["actual_spend"].strip()
        period = row["period"]

        if not actual:
            reason = null_periods.get(period, {}).get("notes", "no reason recorded")
            out.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": "NULL",
                "growth_pct": "",
                "formula": f"not computed — actual_spend is NULL (reason: {reason})",
                "flag": f"NULL: {reason}",
            })
            continue

        cur = float(actual)
        if i == 0:
            out.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": f"{cur:g}",
                "growth_pct": "",
                "formula": "n/a — no previous period",
                "flag": "",
            })
            continue

        prev_raw = filtered[i - 1]["actual_spend"].strip()
        if not prev_raw:
            out.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": f"{cur:g}",
                "growth_pct": "",
                "formula": "n/a — previous period actual_spend is NULL, growth cannot be computed",
                "flag": "",
            })
            continue

        prev = float(prev_raw)
        growth = (cur - prev) / prev * 100.0
        sign = "+" if growth >= 0 else ""
        out.append({
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": f"{cur:g}",
            "growth_pct": f"{sign}{growth:.1f}%",
            "formula": f"(({cur:g} - {prev:g}) / {prev:g}) * 100 = {sign}{growth:.1f}%",
            "flag": "",
        })

    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=False, help="MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        raise SystemExit(
            "REFUSED: --growth-type was not specified. MoM or YoY must be stated "
            "explicitly — never guessing the formula."
        )

    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset['rows'])} rows. "
          f"{len(dataset['nulls'])} null actual_spend rows flagged:")
    for n in dataset["nulls"]:
        print(f"  - {n['period']} {n['ward']} / {n['category']}: {n['notes']}")

    rows = compute_growth(dataset, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["period", "ward", "category", "budgeted_amount",
                        "actual_spend", "growth_pct", "formula", "flag"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Per-ward per-category table written to {args.output} "
          f"({len(rows)} periods).")


if __name__ == "__main__":
    main()
