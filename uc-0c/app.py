import csv

def read_csv(file_path):
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []

def validate_row(row):
    flag = "OK"
    reason = ""
    for key, value in row.items():
        try:
            if key.startswith("amount") or key.startswith("budget") or key.startswith("total"):
                float(value)
        except Exception:
            flag = "NEEDS_REVIEW"
            reason += f"{key} invalid; "
    return {**row, "reason": reason.strip(), "flag": flag}

def check_sums(rows):
    for row in rows:
        total = float(row.get("total", 0))
        sub_sum = sum(float(row.get(k, 0)) for k in row if k.startswith("amount") or k.startswith("budget"))
        if abs(total - sub_sum) > 0.01:
            row["flag"] = "NEEDS_REVIEW"
            row["reason"] += " Sum mismatch."
    return rows

def write_csv(rows, output_file):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    input_file = "data/budget/ward_budget.csv"
    output_file = "growth_output.csv"

    rows = read_csv(input_file)
    validated = [validate_row(row) for row in rows]
    final_rows = check_sums(validated)
    write_csv(final_rows, output_file)

    print(f"Validation complete. Results written to {output_file}")