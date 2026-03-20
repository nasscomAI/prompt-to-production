import argparse

def process_data(text):
    cleaned = text.strip()

    if not cleaned:
        return {
            "result": "",
            "metrics": {"word_count": 0},
            "flag": "NEEDS_REVIEW"
        }

    words = cleaned.split()

    return {
        "result": cleaned,
        "metrics": {
            "word_count": len(words)
        },
        "flag": ""
    }

def main():
    parser = argparse.ArgumentParser(description="UC-0C Data Processor")
    parser.add_argument("--input", required=True, help="Input text")
    args = parser.parse_args()

    output = process_data(args.input)

    print("Processed Output:")
    print(output["result"])
    print("\nMetrics:")
    print(output["metrics"])

    if output["flag"]:
        print("\nFlag:", output["flag"])

if __name__ == "__main__":
    main()
