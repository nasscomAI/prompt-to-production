import argparse

# Skill 1: retrieve_policy
def retrieve_policy(file_path):
    try:
        # FIX: added encoding='utf-8'
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        return content
    except Exception as e:
        return f"Error reading file: {e}"

# Skill 2: summarize_policy
def summarize_policy(lines):
    summary = []
    for line in lines:
        line = line.strip()
        if line:
            # Keep clause as is (no meaning loss)
            summary.append(line)
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    # Step 1: retrieve
    data = retrieve_policy(args.input)

    if isinstance(data, str):
        print(data)
        return

    # Step 2: summarize
    summary = summarize_policy(data)

    # Step 3: save output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print("Summary generated successfully!")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()