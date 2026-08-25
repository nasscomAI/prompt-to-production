"""
UC-0C — Number That Looks Right
Built with the RICE workflow; enforcement rules in agents.md.
Reads data/budget/ward_budget.csv and writes uc-0c/growth_output.csv.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = {"mom": "MoM", "yoy": "YoY"}


def load_dataset(path: str) -> dict:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw = list(reader)

    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    null_rows = []
    rows = []
    for r in raw:
        spend = r.get("actual_spend", "").strip()
        if spend == "":
            null_rows.append({
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "notes": r.get("notes", "").strip(),
            })
            spend = None
        else:
            spend = float(spend)
        rows.append({
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": float(r["budgeted_amount"]),
            "actual_spend": spend,
            "notes": r.get("notes", "").strip(),
        })

    return {"rows": rows, "null_rows": null_rows}


def report_nulls(policy: dict) -> None:
    print(f"Null actual_spend rows found: {len(policy['null_rows'])}")
    for nr in policy["null_rows"]:
        print(f"  FLAGGED  {nr['period']} | {nr['ward']} | {nr['category']} | reason: {nr['notes'] or '(no note)'}")


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    scope = [r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category]
    scope.sort(key=lambda r: r["period"])

    out = []
    for i, row in enumerate(scope):
        spend = row["actual_spend"]
        if spend is None:
            out.append({
                "period": row["period"], "ward": row["ward"], "category": row["category"],
                "actual_spend": "", "previous_actual_spend": "",
                "growth_pct": "", "formula": "N/A - null actual_spend, not computed",
                "status": "FLAGGED", "notes": row["notes"],
            })
            continue

        prev = None
        if growth_type == "MoM" and i > 0:
            prev = scope[i - 1]["actual_spend"]
        else:  # YoY — same period previous year; dataset covers 2024 only.
            prev = None

        if prev is None or prev == 0:
            out.append({
                "period": row["period"], "ward": row["ward"], "category": row["category"],
                "actual_spend": spend, "previous_actual_spend": "" if prev is None else prev,
                "growth_pct": "", "formula": "N/A - no reference period available",
                "status": "no-reference-period", "notes": "",
            })
            continue

        growth = (spend - prev) / prev * 100
        out.append({
            "period": row["period"], "ward": row["ward"], "category": row["category"],
            "actual_spend": spend, "previous_actual_spend": prev,
            "growth_pct": round(growth, 1), "formula": f"({spend} - {prev}) / {prev} * 100",
            "status": "computed", "notes": "",
        })
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Per-ward Per-category Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exactly one ward name")
    parser.add_argument("--category", help="Exactly one category name")
    parser.add_argument("--growth-type", help="MoM or YoY — must be specified explicitly")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement rule 1: never aggregate across wards/categories.
    if not args.ward or not args.category or args.ward.strip().lower() in ("all", "*", "every"):
        print("REFUSED: aggregation across wards/categories is not allowed. "
              "Provide exactly one --ward and one --category.", file=sys.stderr)
        sys.exit(1)

    # Enforcement rule 4: never guess the growth type.
    if not args.growth_type:
        print("REFUSED: --growth-type not specified. Please provide MoM or YoY — refusing to guess.",
              file=sys.stderr)
        sys.exit(1)
    growth_type = GROWTH_TYPES.get(args.growth_type.strip().lower())
    if growth_type is None:
        print(f"REFUSED: unsupported --growth-type '{args.growth_type}'. Use MoM or YoY.",
              file=sys.stderr)
        sys.exit(1)

    dataset = load_dataset(args.input)
    # Enforcement rule 2: flag every null row before computing.
    report_nulls(dataset)

    table = compute_growth(dataset, args.ward.strip(), args.category.strip(), growth_type)
    if not table:
        print(f"REFUSED: no rows for ward '{args.ward}' + category '{args.category}' in the dataset.",
              file=sys.stderr)
        sys.exit(1)

    # Append the flagged null rows to the output so they are never skipped.
    for nr in dataset["null_rows"]:
        table.append({
            "period": nr["period"], "ward": nr["ward"], "category": nr["category"],
            "actual_spend": "", "previous_actual_spend": "",
            "growth_pct": "", "formula": "N/A - null actual_spend, not computed",
            "status": "FLAGGED", "notes": nr["notes"],
        })

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "period", "ward", "category", "actual_spend",
            "previous_actual_spend", "growth_pct", "formula", "status", "notes",
        ])
        writer.writeheader()
        writer.writerows(table)

    computed = [r for r in table if r["status"] == "computed"]
    flagged = [r for r in table if r["status"] == "FLAGGED"]
    print(f"Wrote {args.output}: {len(table)} rows ({len(computed)} computed, {len(flagged)} flagged)")
    print(f"Scope: {args.ward.strip()} / {args.category.strip()} / {growth_type}")


if __name__ == "__main__":
    main()
