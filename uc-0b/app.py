import argparse
import re

TARGET = ["2.3","2.4","2.5","2.6","2.7","3.2","3.4","5.2","5.3","7.2"]

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.S)

    results = []

    for num, body in matches:
        if num in TARGET:

            clean = " ".join(body.split())
            if "Effective:" in clean:
                continue

            clean = clean.replace("═", "")
            clean = clean.replace("|", "")

            clean = re.sub(r'\b\d+\.\s+[A-Z\s]+\b', '', clean)

            results.append(f"{num} {clean.strip()}")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n\n".join(results))

    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()