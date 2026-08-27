"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""

STOPWORDS = {
    "can","i","my","the","a","to","from","when","is","are","for","on","of",
    "what","who","how","do","does","be","with","in","and","use","using"
}

# Intent rules: if all keywords appear in the question, jump directly to that clause
INTENT_RULES = [
    {
        "keywords": {"carry","forward","leave"},
        "doc": "policy_hr_leave.txt",
        "section": "2.6"
    },
    {
        "keywords": {"leave","without","pay"},
        "doc": "policy_hr_leave.txt",
        "section": "5.2"
    },
    {
        "keywords": {"personal","device"},
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1"
    },
    {
        "keywords": {"personal","phone"},
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1"
    },
    {
        "keywords": {"slack","install"},
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3"
    },
    {
        "keywords": {"equipment","allowance"},
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1"
    },
    {
        "keywords": {"meal","da"},
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6"
    }
]


def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


def retrieve_documents(paths):
    docs = {}
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'

    for path in paths:
        name = os.path.basename(path)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        matches = re.findall(pattern, content, re.DOTALL)

        sections = {}

        for num, text in matches:
            clean = " ".join(text.split())
            clean = re.sub(r'\d+\.\s+[A-Z][A-Z\s]+', '', clean)
            sections[num] = clean.strip()

        docs[name] = sections

    return docs


def detect_intent(question_words):
    for rule in INTENT_RULES:
        if rule["keywords"].issubset(question_words):
            return rule
    return None


def answer_question(question, docs):

    words = set(normalize(question).split()) - STOPWORDS

    # Step 1: try explicit intent rules
    rule = detect_intent(words)
    if rule:
        doc = rule["doc"]
        sec = rule["section"]
        if doc in docs and sec in docs[doc]:
            return f"{docs[doc][sec]}\n\nSource: {doc} section {sec}"

    # Step 2: fallback keyword scoring
    best_score = 0
    best_answer = None
    best_doc = None
    best_sec = None

    for doc, sections in docs.items():
        for sec, text in sections.items():
            clause_words = set(normalize(text).split())
            score = len(words & clause_words)

            if score > best_score:
                best_score = score
                best_answer = text
                best_doc = doc
                best_sec = sec

    if best_score < 2:
        return REFUSAL

    return f"{best_answer}\n\nSource: {best_doc} section {best_sec}"


def main():

    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    docs = retrieve_documents(files)

    print("\nPolicy Q&A system ready. Type 'exit' to quit.\n")

    while True:
        question = input("Question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)

        print("\nAnswer:\n")
        print(answer)
        print("\n")


if __name__ == "__main__":
    main()