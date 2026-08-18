import argparse

def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            if line.strip():
                sections.append(line.strip())
        
        return sections

    except Exception as e:
        print("Error reading file:", e)
        return None



def summarize_policy(sections):
    if not sections:
        return "Error: No sections to summarize"

    summary = []

    for section in sections:
        words = section.split()

        if len(words) > 1 and words[0][0].isdigit() and "." in words[0]:
            clause_number = words[0]
            text = " ".join(words[1:])

            short_text = text[:80] + "..." if len(text) > 80 else text

            summary.append(f"Clause {clause_number}: {short_text}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    if sections is None:
        print("Failed to retrieve policy")
        return

    summary = summarize_policy(sections)

    with open(args.output, 'w', encoding='utf-8') as file:
        file.write(summary)

    print("Summary generated successfully!")


if __name__ == "__main__":
    main()