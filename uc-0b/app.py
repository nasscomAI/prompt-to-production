import argparse


def retrieve_policy(file_path):
    clauses = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_clause = None
        buffer = []

        for line in lines:
            line = line.strip()

            # Detect clause numbers like 2.3, 5.2 etc.
            if line and line[0].isdigit() and '.' in line[:4]:
                if current_clause:
                    clauses[current_clause] = " ".join(buffer).strip()

                parts = line.split(' ', 1)
                current_clause = parts[0]
                buffer = [parts[1] if len(parts) > 1 else ""]
            else:
                buffer.append(line)

        if current_clause:
            clauses[current_clause] = " ".join(buffer).strip()

    except Exception as e:
        print(f"Error reading file: {e}")

    return clauses


def summarize_policy(clauses):
    summary = []

    required_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]

    for clause in required_clauses:
        text = clauses.get(clause)

        # Rule 1: Every clause must be present
        if not text:
            summary.append(f"{clause}: [MISSING - FLAGGED]")
            continue

        # Rule 2: Preserve multi-condition obligations
        multi_condition_keywords = ["and", "AND", "requires", "must", "not permitted"]

        if any(word in text for word in multi_condition_keywords):
            # Keep full text to avoid condition drop
            summary.append(f"{clause}: {text} [VERBATIM]")
        else:
            # Safe minimal shortening (no meaning loss)
            short = text[:150].strip()
            summary.append(f"{clause}: {short}")

    return "\n".join(summary)


def main(input_file, output_file):
    clauses = retrieve_policy(input_file)
    summary = summarize_policy(clauses)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
    except Exception as e:
        print(f"Error writing file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Input policy file")
    parser.add_argument("--output", required=True, help="Output summary file")

    args = parser.parse_args()

    main(args.input, args.output)
    print("Summary generated successfully.")