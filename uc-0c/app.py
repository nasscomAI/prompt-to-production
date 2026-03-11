See README.md for run command and expected behaviour.
"""
import argparse
import csv

def main():
    raise NotImplementedError("Build this using your AI tool + RICE prompt")
    parser = argparse.ArgumentParser(description="UC-0C Budget Validator")
    parser.add_argument("--input", required=True, help="Ward budget CSV")
    parser.add_argument("--output", required=True, help="Output file")
    args = parser.parse_args()
    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        results = []
        for row in reader:
            ward = row.get("ward", "unknown")
            numbers = []
            for value in row.values():
                try:
                    numbers.append(float(value))
                except:
                    pass
            flag = "ok"
            for num in numbers:
                if num > 10000000:
                    flag = "suspicious"
            results.append({
                "ward": ward,
                "flag": flag
            })
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ward", "flag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    main()
