import argparse


# ✅ Step 1: Read policy file
def retrieve_policy(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


# ✅ Step 2: Extract required clauses
def extract_clauses(lines):
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7",
                        "3.2", "3.4", "5.2", "5.3", "7.2"]

    extracted = []

    for line in lines:
        line = line.strip()
        for clause in required_clauses:
            if line.startswith(clause):
                extracted.append(line)

    return extracted


# ✅ Step 3: Validate clauses
def validate_clauses(clauses):
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7",
                        "3.2", "3.4", "5.2", "5.3", "7.2"]

    found = [c.split()[0] for c in clauses]

    for clause in required_clauses:
        if clause not in found:
            raise ValueError(f"Missing clause: {clause}")

    # 🔥 Special check for Clause 5.2 (two approvals)
    for c in clauses:
        if c.startswith("5.2"):
            if "Department Head" not in c or "HR Director" not in c:
                raise ValueError("Clause 5.2 missing required approvals")

    return True


# ✅ Step 4: Write summary
def write_summary(output_path, clauses):
    with open(output_path, 'w') as file:
        for c in clauses:
            file.write(c + "\n")


# ✅ Main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    lines = retrieve_policy(args.input)

    if lines is None:
        return

    clauses = extract_clauses(lines)

    try:
        validate_clauses(clauses)
    except Exception as e:
        print(f"Validation Error: {e}")
        return

    write_summary(args.output, clauses)

    print("Summary generated successfully.")


if __name__ == "__main__":
    main()