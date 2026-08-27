"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCUMENT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

SECTION_HEADER_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S.*)$")
WORD_RE = re.compile(r"\w+")
PHRASE_EXPANSIONS = {
    "leave without pay": "lwp",
    "work laptop": "corporate device",
    "company laptop": "corporate device",
    "personal phone": "personal device",
    "personal mobile": "personal device",
    "work-from-home": "work from home",
}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "can", "do", "for", "from", "have", "i", "if", "in", "is",
    "it", "my", "not", "of", "on", "or", "our", "please", "so",
    "that", "the", "this", "to", "was", "will", "with", "you",
}


def normalize_text(text):
    normalized = text.lower()
    for phrase, replacement in PHRASE_EXPANSIONS.items():
        normalized = normalized.replace(phrase, replacement)
    return normalized


def normalize_token(token):
    token = token.lower()
    if token.endswith("ing") and len(token) > 4:
        token = token[:-3]
    elif token.endswith("ed") and len(token) > 3:
        token = token[:-2]
    elif token.endswith("es") and len(token) > 3:
        token = token[:-2]
    elif token.endswith("s") and len(token) > 2:
        token = token[:-1]
    if token.endswith("al") and len(token) > 4:
        token = token[:-2]
    return token


def tokenize(text):
    normalized = normalize_text(text)
    return [normalize_token(token) for token in WORD_RE.findall(normalized) if normalize_token(token) not in STOPWORDS]


def build_token_weights(documents):
    token_counts = {}
    for document in documents:
        for section in document["sections"]:
            tokens = set(tokenize(section["text"]))
            for token in tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
    weights = {}
    for token, count in token_counts.items():
        weights[token] = 1.0 / count
    return weights


def retrieve_documents(document_paths):
    documents = []
    top_section_re = re.compile(r"^\s*\d+\.\s+.*$")
    for path in document_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Document not found: {path}")
        name = os.path.basename(path)
        sections = []
        current_section = None
        current_lines = []
        with open(path, "r", encoding="utf-8") as input_file:
            for raw_line in input_file:
                line = raw_line.rstrip("\n")
                stripped = line.strip()
                match = SECTION_HEADER_RE.match(line)
                if match:
                    if current_section is not None:
                        sections.append({
                            "section": current_section,
                            "text": " ".join(current_lines).strip(),
                        })
                    current_section = match.group(1)
                    current_lines = [match.group(2).strip()]
                elif current_section is not None:
                    if not stripped:
                        continue
                    if top_section_re.match(line):
                        continue
                    if all(not char.isalnum() for char in stripped):
                        continue
                    current_lines.append(stripped)
            if current_section is not None:
                sections.append({
                    "section": current_section,
                    "text": " ".join(current_lines).strip(),
                })
        documents.append({"name": name, "sections": sections})
    return {"documents": documents}


def score_text(question, text):
    question_tokens = set(tokenize(question))
    section_tokens = set(tokenize(text))
    score = len(question_tokens & section_tokens)

    qnorm = normalize_text(question)
    tnorm = normalize_text(text)
    phrase_bonus_phrases = ["personal device", "corporate device", "lwp"]
    for phrase in phrase_bonus_phrases:
        if phrase in qnorm and phrase in tnorm:
            score += 2

    return score


def answer_question(question, documents):
    best_doc = None
    best_section = None
    best_score = 0
    second_best_score = 0

    for document in documents:
        doc_best_section = None
        doc_best_score = 0
        for section in document["sections"]:
            score = score_text(question, section["text"])
            if score > doc_best_score:
                doc_best_score = score
                doc_best_section = section
        if doc_best_score > best_score:
            second_best_score = best_score
            best_score = doc_best_score
            best_doc = document
            best_section = doc_best_section
        elif doc_best_score == best_score and doc_best_score > 0:
            second_best_score = doc_best_score

    if best_score < 2 or second_best_score == best_score:
        return {
            "answer": REFUSAL_TEMPLATE,
            "citation": "",
            "refusal": True,
        }

    citation = f"{best_doc['name']} section {best_section['section']}"
    answer = f"{best_section['text']} (Source: {citation})"
    return {"answer": answer, "citation": citation, "refusal": False}


def main():
    documents = retrieve_documents(DOCUMENT_PATHS)["documents"]
    print("Policy documents loaded. Ask a question or type 'exit' to quit.")

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        response = answer_question(question, documents)
        print(response["answer"])
        print()


if __name__ == "__main__":
    main()
