import argparse

# --- Skills Implementation ---
def retrieve_policy(file_path):
    """
    Reads the policy document from the given file path.
    Returns the text content as a string.
    Error handling: Raises FileNotFoundError if the file doesn't exist.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        raise

def summarize_policy(policy_text):
    """
    Summarizes the HR policy text while preserving all binding obligations.
    Error handling: If text is empty, returns a message indicating no content.
    """
    if not policy_text.strip():
        return "No content to summarize."

    # Simple placeholder summarization logic: 
    # For a real implementation, you can integrate AI summarization here
    lines = policy_text.strip().split('\n')
    summary = []
    for line in lines:
        line = line.strip()
        if line:  # skip empty lines
            summary.append(line)
    # Join lines for output
    return "\n".join(summary)

# --- Main Script ---
def main():
    parser = argparse.ArgumentParser(description="UC-0B: Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    args = parser.parse_args()

    # Step 1: Retrieve policy
    policy_text = retrieve_policy(args.input)

    # Step 2: Summarize policy
    summary_text = summarize_policy(policy_text)

    # Step 3: Save summary to output file
    with open(args.output, 'w', encoding='utf-8') as out_file:
        out_file.write(summary_text)

    print(f"Summary completed! Output saved to {args.output}")

if __name__ == "__main__":
    main()