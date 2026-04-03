import argparse

def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            clauses = text.split("\n")
            return [c.strip() for c in clauses if c.strip()]
    except Exception as e:
        print("ERROR:", e)
        return None
def summarize_policy(clauses):
    if not clauses:
        return "ERROR: No content"

    summary = []

    for clause in clauses:
        # Keep important lines (must, requires, not permitted etc.)
        if any(word in clause.lower() for word in ["must", "requires", "required", "not permitted", "will", "forfeited"]):
            summary.append(clause)

    # If nothing detected, return all (to avoid clause omission)
    if not summary:
        summary = clauses

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    if clauses is None:
        print("Error reading file")
        return

    summary = summarize_policy(clauses)

    with open(args.output, "w") as f:
        f.write(summary)

    print("Summary generated successfully!")


if __name__ == "__main__":
    main()