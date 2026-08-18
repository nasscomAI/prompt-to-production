import argparse
import re

def retrieve_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def extract_clause(policy_text, clause_num):
    lines = policy_text.splitlines()
    clause_text_parts = []
    found = False
    
    for line in lines:
        stripped_line = line.strip()
        if not found:
            if line.startswith(f"{clause_num} ") or line.startswith(f"{clause_num}\t"):
                found = True
                content = line[len(clause_num):].strip()
                clause_text_parts.append(content)
        else:
            if line.startswith(" ") or line.startswith("\t"):
                clause_text_parts.append(stripped_line)
            elif stripped_line == "":
                continue
            else:
                break
                
    if found:
        return " ".join(clause_text_parts).strip()
    return None


def summarize_policy(policy_text):
    important_clauses = [
        "2.3",
        "2.4",
        "2.5",
        "2.6",
        "2.7",
        "3.2",
        "3.4",
        "5.2",
        "5.3",
        "7.2"
    ]

    summary_lines = []

    for clause in important_clauses:
        text = extract_clause(policy_text, clause)
        if text:
            summary_lines.append(
                f"Clause {clause}: {text}"
            )
        else:
            summary_lines.append(
                f"Clause {clause}: NOT FOUND"
            )

    return "\n\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    policy_text = retrieve_policy(
        args.input
    )

    summary = summarize_policy(
        policy_text
    )

    with open(
        args.output,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(summary)

    print(
        f"Summary written to {args.output}"
    )

if __name__ == "__main__":
    main()
