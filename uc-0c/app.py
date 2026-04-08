import argparse
import re

def extract_numbers(text: str):
    """Pull numeric values from text."""
    return re.findall(r"\d+", text)

def validate_range(numbers):
    """Check if numbers are within expected ranges."""
    results = []
    for n in numbers:
        try:
            value = int(n)
            if 0 <= value <= 1000000:
                results.append((value, "valid"))
            else:
                results.append((value, "invalid"))
        except ValueError:
            results.append((n, "error"))
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input text file")
    parser.add_argument("--output", required=True, help="Path to output results file")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as infile:
        text = infile.read()

    numbers = extract_numbers(text)
    results = validate_range(numbers)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write("Extracted Numbers and Validation:\n")
        for value, status in results:
            outfile.write(f"{value} → {status}\n")

    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
