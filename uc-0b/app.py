import argparse

def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return "Error reading file"

def summarize(text):
    if not text or text.startswith("Error"):
        return text

    lines = text.split("\n")
    summary = []

    for line in lines:
        line = line.strip()
        if line:
            summary.append(line)

    return "\n".join(summary[:10])

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    text = read_file(args.input)
    summary = summarize(text)
    write_file(args.output, summary)

    print("Summary created successfully!")

if __name__ == "__main__":
    main()