"""
UC-0C — Number That Looks Right
Infrastructure spend growth calculator per agents.md and skills.md.
Computes per-ward per-category MoM growth. Never aggregates across wards/categories.
"""
import argparse
import csv


def load_dataset(file_path: str) -> dict:
    """
    Reads ward_budget CSV, validates columns, and reports all null actual_spend
    rows before returning. Returns {data, null_rows, total_rows}.
    """
    required_cols = {"period", "ward", "category", "actual_spend", "notes"}

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    if not rows:
        raise ValueError("Dataset is empty.")

    missing = required_cols - set(rows[0].keys())
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    null_rows = []
    for row in rows:
        if row.get("actual_spend", "").strip() == "":
            null_rows.append({
                "period":   row["period"],
                "ward":     row["ward"],
                "category": row["category"],
                "notes":    row.get("notes", ""),
            })

    return {"data": rows, "null_rows": null_rows, "total_rows": len(rows)}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM growth strictly for one ward + one category.
    Flags null rows — never computes growth from a null value.
    Shows formula in every output row.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type '{growth_type}' is not valid. "
            "Please specify 'MoM' or 'YoY' explicitly — the system will not guess."
        )

    filtered = [
        r for r in dataset["data"]
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        raise ValueError(
            f"No rows found for ward='{ward}', category='{category}'. "
            "Check that spelling matches the dataset exactly."
        )

    filtered.sort(key=lambda r: r["period"])

    if growth_type == "MoM":
        formula_label = "((current - previous) / previous) * 100"
        step = 1
    else:  # YoY — compare same month previous year (not present in 2024-only dataset, handled gracefully)
        formula_label = "((current_year - prior_year) / prior_year) * 100"
        step = 12

    results = []
    for i, row in enumerate(filtered):
        spend_str = row["actual_spend"].strip()
        is_null = spend_str == ""
        current_spend = None if is_null else float(spend_str)

        if i < step:
            flag = f"NULL — {row.get('notes', '').strip()}" if is_null else ""
            results.append({
                "period":         row["period"],
                "ward":           row["ward"],
                "category":       row["category"],
                "actual_spend":   "" if is_null else current_spend,
                "previous_spend": "N/A (no prior period)",
                "formula":        formula_label,
                "growth_pct":     "N/A (no prior period)",
                "flag":           flag,
            })
            continue

        prev_row = filtered[i - step]
        prev_str = prev_row["actual_spend"].strip()
        prev_null = prev_str == ""
        prev_spend = None if prev_null else float(prev_str)

        flag_parts = []
        if is_null:
            flag_parts.append(f"current NULL — {row.get('notes', '').strip()}")
        if prev_null:
            flag_parts.append(f"previous NULL — {prev_row.get('notes', '').strip()}")

        if is_null or prev_null:
            results.append({
                "period":         row["period"],
                "ward":           row["ward"],
                "category":       row["category"],
                "actual_spend":   "" if is_null else current_spend,
                "previous_spend": "" if prev_null else prev_spend,
                "formula":        formula_label,
                "growth_pct":     "NULL — cannot compute",
                "flag":           "; ".join(flag_parts),
            })
        else:
            growth = ((current_spend - prev_spend) / prev_spend) * 100
            results.append({
                "period":         row["period"],
                "ward":           row["ward"],
                "category":       row["category"],
                "actual_spend":   current_spend,
                "previous_spend": prev_spend,
                "formula":        formula_label,
                "growth_pct":     f"{growth:+.1f}%",
                "flag":           "",
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Infrastructure Spend Growth Calculator")
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True, help="Ward name (exact match)")
    parser.add_argument("--category",    required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output",      required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    print(f"Loaded {dataset['total_rows']} rows from dataset.")

    if dataset["null_rows"]:
        print(f"\n[NULL REPORT] {len(dataset['null_rows'])} null actual_spend row(s) flagged before computation:")
        for nr in dataset["null_rows"]:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | notes: {nr['notes']}")
    else:
        print("No null rows detected.")

    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    fieldnames = [
        "period", "ward", "category", "actual_spend",
        "previous_spend", "formula", "growth_pct", "flag"
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Output written to {args.output}")
    print(f"Rows: {len(results)} | Ward: {args.ward} | Category: {args.category} | Type: {args.growth_type}")


if __name__ == "__main__":
    main()
