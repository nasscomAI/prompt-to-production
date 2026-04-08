import argparse

def extract_clauses(text):
    # Split complaint into clauses using simple separators
    separators = [".", ",", "and", "but"]
    clauses = [text]

    for sep in separators:
        temp = []
        for clause in clauses:
            temp.extend(clause.split(sep))
        clauses = temp

    # Clean and remove empty clauses
    clauses = [c.strip() for c in clauses if c.strip()]
    return clauses


def process_complaint(text):
    clauses = extract_clauses(text)

    if not clauses:
        return {
            "clauses": [text],
            "flag": "NEEDS_REVIEW"
        }

    return {
        "clauses": clauses,
        "flag": ""
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0B Clause Extraction")
    parser.add_argument("--text", required=True, help="Complaint text")
    args = parser.parse_args()

    result = process_complaint(args.text)

    print("Clauses:")
    for i, clause in enumerate(result["clauses"], 1):
        print(f"{i}. {clause}")

    if result["flag"]:
        print("Flag:", result["flag"])


if __name__ == "__main__":
    main()
