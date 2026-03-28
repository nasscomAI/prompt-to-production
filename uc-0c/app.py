import argparse
import csv
import os


def compute_growth(rows, ward, category):
    filtered = [
        r for r in rows
        if r.get("ward") == ward and r.get("category") == category
    ]

    if len(filtered) < 2:
        return []

    results = []

    for i in range(1, len(filtered)):
        try:
            prev = float(filtered[i - 1]["amount"])
            curr = float(filtered[i]["amount"])
        except:
            continue

        if prev == 0:
            growth = 0
        else:
            growth = ((curr - prev) / prev) * 100

        results.append({
            "ward": ward,
            "category": category,
            "growth": round(growth, 2)
        })

    return results


def process_file(input_path, ward, category, output_path):
    if not os.path.exists(input_path):
        print("Error: file not found")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = compute_growth(rows, ward, category)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ward", "category", "growth"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth output saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    process_file(
        args.input,
        args.ward,
        args.category,
        args.output
    )