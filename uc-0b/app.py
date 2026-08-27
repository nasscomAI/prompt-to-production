import argparse

def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        clauses = []
        current_clause = ""
        
        for line in lines:
            line = line.strip()
            if line:
                if line[0].isdigit():  # new clause starts
                    if current_clause:
                        clauses.append(current_clause)
                    current_clause = line
                else:
                    current_clause += " " + line
        
        if current_clause:
            clauses.append(current_clause)
        
        return clauses

    except Exception as e:
        print("Error reading file:", e)
        return None


def summarize_policy(clauses):
    if not clauses:
        return None

    summary = []
    
    for clause in clauses:
        summary.append(clause)

    return summary


def write_output(output_path, summary):
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in summary:
            f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    if summary:
        write_output(args.output, summary)
        print("Summary generated successfully!")
    else:
        print("Failed to generate summary")


if __name__ == "__main__":
    main()