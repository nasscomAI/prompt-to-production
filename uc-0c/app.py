import argparse
import csv
import os
from typing import List, Dict, Any

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    if not args.ward or not args.category:
        print("Refusing: ward and category must be specified; no cross-ward/category aggregation.")
        return
    if not args.growth_type:
        print("Refusing: --growth-type is required and must be MoM or YoY.")
        return
    growth_type = args.growth_type.strip()
    if growth_type not in ("MoM", "YoY"):
        print("Refusing: --growth-type must be MoM or YoY.")
        return
    records, report = load_dataset(args.input)
    table = compute_growth(records, args.ward, args.category, growth_type)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        cols = ["period", "ward", "category", "actual_spend", "comparator_period", "comparator_actual", "growth_value", "growth_percent", "formula", "flag", "notes"]
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for row in table:
            writer.writerow(row)
    print(f"Wrote {len(table)} rows to {args.output}")

def load_dataset(path: str) -> (List[Dict[str, Any]], Dict[str, Any]):
    records: List[Dict[str, Any]] = []
    report = {"total_rows": 0, "null_rows": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                report["total_rows"] += 1
                period = r.get("period", "").strip()
                ward = r.get("ward", "").strip()
                category = r.get("category", "").strip()
                notes = (r.get("notes") or "").strip()
                as_val = r.get("actual_spend")
                as_num = None
                if as_val is not None and str(as_val).strip() != "":
                    try:
                        as_num = float(as_val)
                    except Exception:
                        as_num = None
                else:
                    report["null_rows"].append({"period": period, "ward": ward, "category": category, "notes": notes})
                records.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": float(r.get("budgeted_amount")) if r.get("budgeted_amount") else None,
                    "actual_spend": as_num,
                    "notes": notes,
                })
    except Exception:
        return [], {"error": "file_unreadable"}
    return records, report

def month_key(period: str) -> int:
    try:
        y, m = period.split("-")
        return int(y) * 100 + int(m)
    except Exception:
        return 0

def norm_name(s: str) -> str:
    if s is None:
        return ""
    t = s.strip().lower()
    t = t.replace("_", " ")
    t = t.replace("&", "and")
    t = t.replace("–", "-").replace("—", "-")
    t = " ".join(t.split())
    return t

def compute_growth(records: List[Dict[str, Any]], ward: str, category: str, growth_type: str) -> List[Dict[str, Any]]:
    if not ward or not category:
        return []
    w_norm = norm_name(ward)
    c_norm = norm_name(category)
    recs = [r for r in records if norm_name(r.get("ward")) == w_norm and norm_name(r.get("category")) == c_norm]
    recs.sort(key=lambda r: month_key(r.get("period", "")))
    out: List[Dict[str, Any]] = []
    index = {r["period"]: r for r in recs}
    months = [r["period"] for r in recs]
    for i, p in enumerate(months):
        cur = index[p]
        cur_val = cur.get("actual_spend")
        notes = cur.get("notes") or ""
        comp_period = None
        comp_val = None
        if growth_type == "MoM":
            if i > 0:
                comp_period = months[i - 1]
                comp_val = index[comp_period].get("actual_spend")
        else:
            print("Refusing: YoY not supported for single-year dataset.")
            return []
        flag = ""
        growth_value = ""
        growth_percent = ""
        formula = ""
        if cur_val is None or comp_val is None:
            flag = "NULL_VALUE"
            formula = "(current - previous)/previous"
        else:
            try:
                growth = (cur_val - comp_val) / comp_val if comp_val != 0 else None
            except Exception:
                growth = None
            if growth is None:
                flag = "DIV_BY_ZERO"
                formula = "(current - previous)/previous"
            else:
                growth_value = round(growth, 6)
                pct = round(growth * 100.0, 1)
                sign = "+" if pct >= 0 else ""
                growth_percent = f"{sign}{pct}%"
                formula = "(current - previous)/previous"
        out.append({
            "period": p,
            "ward": ward,
            "category": category,
            "actual_spend": "" if cur_val is None else cur_val,
            "comparator_period": "" if comp_period is None else comp_period,
            "comparator_actual": "" if comp_val is None else comp_val,
            "growth_value": growth_value,
            "growth_percent": growth_percent,
            "formula": formula,
            "flag": flag,
            "notes": notes,
        })
    return out

if __name__ == "__main__":
    main()
