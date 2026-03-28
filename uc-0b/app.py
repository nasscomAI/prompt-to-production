import argparse

def retrieve_policy(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # simple split by clauses
    clauses = content.split('\n')
    return [c.strip() for c in clauses if c.strip()]


def summarize_policy(clauses):
    summary = []
    
    for clause in clauses:
        # keep clause intact (safe approach)
        summary.append(clause)
    
    return "\n".join(summary)


def main(input_file, output_file):
    clauses = retrieve_policy(input_file)
    summary = summarize_policy(clauses)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    main(args.input, args.output)