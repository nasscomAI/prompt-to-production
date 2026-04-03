import argparse

def retrieve_policy(file_path):
    try:
        # FIX: added encoding='utf-8'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        clauses = []
        current_clause = None
        current_text = ""

        for line in lines:
            line = line.strip()
            if line and line[0].isdigit():
                if current_clause:
                    clauses.append((current_clause, current_text.strip()))
                parts = line.split(" ", 1)
                current_clause = parts[0]
                current_text = parts[1] if len(parts) > 1 else ""
            else:
                current_text += " " + line

        if current_clause:
            clauses.append((current_clause, current_text.strip()))

        return clauses

    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def summarize_policy(clauses):
    required_clauses = ["2.3","2.4","2.5","2.6","2.7","3.2","3.4","5.2","5.3","7.2"]
    found = {c: False for c in required_clauses}
    summary = []

    for clause, text in clauses:
        if clause in found:
            found[clause] = True
            summary.append(f"{clause}: {text}")

    missing = [c for c,v in found.items() if not v]
    if missing:
        return f"Error: Missing clauses {missing}"

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding='utf-8') as f:
        f.write(summary)

    print("Done ✅")


if __name__ == "__main__":
    main()