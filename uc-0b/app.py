import os

INPUT_FILE = "../data/policy-documents/policy_hr_leave.txt"
OUTPUT_FILE = "summary_hr_leave.txt"

def read_policy(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_clauses(text):
    lines = text.split('\n')
    clauses = []
    current_clause = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_clause:
                clauses.append('\n'.join(current_clause))
                current_clause = []
        else:
            current_clause.append(stripped)
    if current_clause:
        clauses.append('\n'.join(current_clause))
    return clauses

def summarize_clause(clause):
    lines = clause.split('\n')
    header = lines[0]
    body = ' '.join(lines[1:]) if len(lines) > 1 else ''
    if len(body) > 300:
        body = body[:300] + '...'
    if body:
        return f"{header}\n  {body}"
    return header

def write_summary(clauses, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("HR LEAVE POLICY — SUMMARY\n")
        f.write("=" * 40 + "\n\n")
        for i, clause in enumerate(clauses, 1):
            summary = summarize_clause(clause)
            f.write(f"[Clause {i}]\n{summary}\n\n")
    print(f"Done! {len(clauses)} clauses summarized → {output_file}")

def main():
    print(f"Reading: {INPUT_FILE}")
    text = read_policy(INPUT_FILE)
    clauses = extract_clauses(text)
    print(f"Found {len(clauses)} clauses")
    write_summary(clauses, OUTPUT_FILE)

if __name__ == "__main__":
    main()