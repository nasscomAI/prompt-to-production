"""
UC-X — Ask My Documents
CRAFT-enforced: cross-document blending, hedged hallucination, condition dropping.
"""
import os
import re

POLICY_FILES = {
    "policy_hr_leave.txt":             "HR-POL-001",
    "policy_it_acceptable_use.txt":    "IT-POL-003",
    "policy_finance_reimbursement.txt": "FIN-POL-007",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/policy-documents")

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "generally", "usually", "often",
]

MIN_SCORE = 1  # minimum keyword hits to count as a match

STOP = {"the", "a", "an", "is", "can", "i", "my", "for", "on", "in",
        "to", "do", "of", "and", "or", "be", "are", "at", "it", "what",
        "who", "how", "when", "same", "use", "with", "from", "that",
        "this", "which", "their", "there"}

# Expand question words to catch morphological variants in policy text
QUERY_EXPANSION = {
    "phone":    {"device", "devices", "personal"},
    "phones":   {"device", "devices"},
    "install":  {"software", "installation"},
    "approves": {"approval"},
    "approve":  {"approval"},
    "approved": {"approval"},
    "files":    {"access"},
}

# When question asks "who", sections naming specific roles score much higher
WHO_ROLE_SIGNALS = ["department head", "hr director", "municipal commissioner",
                    "finance director", "manager approval", "it department"]


def retrieve_documents(data_dir: str) -> dict:
    index = {}
    pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+\s|\n[═]+|\Z)', re.DOTALL | re.MULTILINE)

    for filename, ref in POLICY_FILES.items():
        path = os.path.join(data_dir, filename)
        with open(path, encoding="utf-8") as f:
            content = f.read()

        sections = []
        for match in pattern.finditer(content):
            section_id = match.group(1).strip()
            text = " ".join(match.group(2).split())
            if text:
                sections.append({"section_id": section_id, "text": text})

        index[filename] = {"ref": ref, "sections": sections}

    return index


def _score_section(unigrams: set, bigrams: set, section_text: str, is_who_question: bool = False) -> float:
    text_lower = section_text.lower()
    # Unigram: word-boundary match scores 1 each
    uni_score = sum(1 for t in unigrams if re.search(r'\b' + re.escape(t) + r'\b', text_lower))
    # Bigram: adjacent pair match scores 2 each (higher precision)
    bi_score  = sum(2 for bg in bigrams if re.search(r'\b' + re.escape(bg) + r'\b', text_lower))
    # "Who" questions: heavily boost sections that name specific approver roles
    who_score = 0
    if is_who_question:
        who_score = sum(5 for sig in WHO_ROLE_SIGNALS if sig in text_lower)
    return uni_score + bi_score + who_score


def answer_question(question: str, index: dict) -> str:
    question_lower = question.lower()
    words = re.findall(r'\b\w+\b', question_lower)
    base_unigrams = {w for w in words if w not in STOP and len(w) > 2}
    # Expand with synonyms to handle morphological variants in policy text
    expanded = set(base_unigrams)
    for w in base_unigrams:
        expanded.update(QUERY_EXPANSION.get(w, set()))
    unigrams = expanded
    bigrams  = {f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)
                if words[i] not in STOP and words[i+1] not in STOP
                and len(words[i]) > 2 and len(words[i+1]) > 2}

    is_who_question = question_lower.startswith("who")
    # Dynamic threshold: longer questions need more evidence to avoid weak matches
    min_score = 2 if len(base_unigrams) >= 4 else MIN_SCORE

    best_score = 0
    best_doc = None
    best_section = None

    for filename, data in index.items():
        for sec in data["sections"]:
            score = _score_section(unigrams, bigrams, sec["text"], is_who_question)
            if score > best_score:
                best_score = score
                best_doc = filename
                best_section = sec

    if best_score < min_score or best_section is None:
        return REFUSAL_TEMPLATE

    ref = index[best_doc]["ref"]
    return (
        f"Source: {best_doc} ({ref}) | Section {best_section['section_id']}:\n"
        f"{best_section['text']}"
    )


def main():
    print("UC-X — Ask My Documents")
    print("Policy documents loaded: HR-POL-001, IT-POL-003, FIN-POL-007")
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    index = retrieve_documents(DATA_DIR)

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Exiting.")
            break

        answer = answer_question(question, index)
        print(f"\nA: {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
