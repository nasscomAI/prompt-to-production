import argparse

def retrieve_policy(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def summarize_policy(text):
    # simple safe summary (no loss)
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)

    with open(args.output, 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    main()
