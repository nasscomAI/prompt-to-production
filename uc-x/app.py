
import os
import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""

FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

def load_documents():
    docs = {}
    for file in FILES:
        if not os.path.exists(file):
            print(f"Error: {file} not found.")
            exit(1)

        with open(file, "r", encoding="utf-8") as f:
            docs[file] = f.read()
    return docs

def split_sections(text):
    sections = {}
    current = "Introduction"
    buffer = []

    for line in text.splitlines():
        m = re.match(r"^(\d+\.\d+)\s+(.*)", line.strip())
        if m:
            if buffer:
                sections[current] = "\n".join(buffer)
            current = m.group(1)
            buffer = [line]
        else:
            buffer.append(line)

    if buffer:
        sections[current] = "\n".join(buffer)

    return sections

def search(question, docs):
    question = question.lower()

    found = []

    for doc_name, text in docs.items():
        sections = split_sections(text)

        for section, content in sections.items():
            score = 0
            for word in re.findall(r"[a-zA-Z]+", question):
                if len(word) < 3:
                    continue
                if word in content.lower():
                    score += 1

            if score:
                found.append((score, doc_name, section, content))

    if not found:
        return REFUSAL

    found.sort(reverse=True)

    best = found[0]

    if len(found) > 1 and found[1][0] == best[0] and found[1][1] != best[1]:
        return REFUSAL

    _, doc, section, content = best

    answer = content.strip().split("\n")[0]

    return f"""{answer}

Source: {doc} | Section {section}"""

def main():
    docs = load_documents()

    print("=" * 60)
    print("CMC Policy Assistant")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:
        question = input("\nAsk a question: ").strip()

        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        print()
        print(search(question, docs))

if __name__ == "__main__":
    main()
