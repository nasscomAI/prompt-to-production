"""
UC-0C — Number That Looks Right
Enforcement rules (from agents.md / skills.md):
- Never aggregate across wards or categories unless explicitly instructed.
- Flag every null actual_spend row with its reason from notes; never impute.
- Show the formula used in every output row.
- Refuse if --growth-type is not specified; never guess MoM or YoY.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
ALLOWED_GROWTH_TYPES = ["MoM", "YoY"]


def load_dataset(input_path: str) -> list[dict]:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    null_rows = [r for r in rows if (r.get("actual_spend") or "").strip() == ""]
    return {"rows": rows, "null_rows": null_rows}


def compute_growth(rows: list[dict], null_rows: list[dict], ward: str, category: str, growth_type: str) -> list[str]:
    def to_num(v):
        v = (v or "").strip()
        return float(v.replace(",", "")) if v else None

    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError(f"Growth type must be one of {ALLOWED_GROWTH_TYPES}; got '{growth_type}'")

    sel = [r for r in rows if r["ward"] == ward and r["category"] == category]
    sel.sort(key=lambda r: r["period"])

    flag_prev = ""
    out = []
    if growth_type == "MoM":
        default_formula = "MoM = (actual_spend[current month] - actual_spend[previous month]) / actual_spend[previous month] * 100"
        prev = None
        for r in sel:
            cur = to_num(r["actual_spend"])
            period = r["period"]
            if cur is None:
                out.append(f"{period}|{ward}|{category}|NULL|FLAG: {r['notes']}")
                prev = None
                continue
            if prev is None:
                out.append(f"{period}|{ward}|{category}|n/a ({default_formula}; no prior month)|FORMULA: {default_formula}")
            else:
                growth = (cur - prev) / prev * 100
                out.append(f"{period}|{ward}|{category}|{growth:.1f}%|FORMULA: {default_formula}")
            prev = cur
    else:  # YoY
        default_formula = "YoY = (actual_spend[current year] - actual_spend[same month previous year]) / actual_spend[same month previous year] * 100"
        prev_map = {}
        for r in sel:
            cur = to_num(r["actual_spend"])
            if cur is None:
                out.append(f"{r['period']}|{ward}|{category}|NULL|FLAG: {r['notes']}")
                continue
            month = r["period"][5:7]
            if month not in prev_map:
                prev_map[month] = cur
                out.append(f"{r['period']}|{ward}|{category}|n/a ({default_formula}; no prior-year month)|FORMULA: {default_formula}")
            else:
                growth = (cur - prev_map[month]) / prev_map[month] * 100
                out.append(f"{r['period']}|{ward}|{category}|{growth:.1f}%|FORMULA: {default_formula}")
            prev_map[month] = cur

    out.insert(0, f"period|ward|category|value|formula({growth_type})")
    null_header = [f"NULL_FLAG|{r['period']}|{r['ward']}|{r['category']}|{r['notes']}" for r in null_rows]
    out.extend(null_header)
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", required=True, help="Category")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY (required)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    data = load_dataset(args.input)
    if args.growth_type not in ALLOWED_GROWTH_TYPES:
        sys.exit(f"REFUSED: --growth-type must be one of {ALLOWED_GROWTH_TYPES}. Please specify MoM or YoY.")

    matched = [r for r in data["rows"] if r["ward"] == args.ward and r["category"] == args.category]
    if not matched:
        sys.exit(f"REFUSED: No rows found for ward '{args.ward}' and category '{args.category}'.")

    # Nulls relevant to requested scope are flagged inside compute_growth via sel; global nulls are reported too.
    nulls_in_scope = [r for r in data["null_rows"] if r["ward"] == args.ward and r["category"] == args.category]
    lines = compute_growth(data["rows"], nulls_in_scope, args.ward, args.category, args.growth_type)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nDone. Results written to {args.output}")


if __name__ == "__main__":
    main()
