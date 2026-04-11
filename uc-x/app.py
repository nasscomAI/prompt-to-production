import os

POLICY_FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

REFUSAL_TRIGGERS = [
    "flexible working culture",
    "personal phone",
    "phone for work",
    "phone to access work",
]

SECTION_KEYWORDS = {
    "policy_hr_leave.txt": [
        "annual leave", "carry forward", "sick leave", "maternity",
        "paternity", "leave without pay", "lwp", "encashment",
        "grievance", "leave application", "loss of pay", "lop",
        "approves leave", "who approves"
    ],
    "policy_it_acceptable_use.txt": [
        "install", "software", "laptop", "corporate device",
        "slack", "it department", "endpoint", "acceptable use",
        "work laptop", "personal device"
    ],
    "policy_finance_reimbursement.txt": [
        "allowance", "reimbursement", "da ", "daily allowance",
        "meal", "receipt", "home office", "equipment", "travel",
        "claim", "finance", "outstation"
    ],
}


def retrieve_documents():
    docs = {}
    for name, path in POLICY_FILES.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing file: {name} at {path}")
        with open(path, "r", encoding="utf-8") as f:
            docs[name] = f.read()
    return docs


def get_best_paragraph(question_lower, content):
    words = [w for w in question_lower.split() if len(w) > 2]
    best_para = ""
    best_score = 0
    for para in content.split("\n\n"):
        score = sum(1 for w in words if w in para.lower())
        if score > best_score:
            best_score = score
            best_para = para.strip()
    return best_para, best_score


def answer_question(question, docs):
    question_lower = question.lower()

    # explicit refusal triggers
    for trigger in REFUSAL_TRIGGERS:
        if trigger in question_lower:
            return REFUSAL_TEMPLATE

    # match to specific doc using domain keywords
    doc_scores = {}
    for doc_name, keywords in SECTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in question_lower)
        if score > 0:
            doc_scores[doc_name] = score

    if not doc_scores:
        return REFUSAL_TEMPLATE

    # if multiple docs match check dominance
    if len(doc_scores) > 1:
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_docs[0][1] > sorted_docs[1][1]:
            best_doc = sorted_docs[0][0]
        else:
            return REFUSAL_TEMPLATE
    else:
        best_doc = list(doc_scores.keys())[0]

    best_para, _ = get_best_paragraph(question_lower, docs[best_doc])

    if not best_para:
        return REFUSAL_TEMPLATE

    for phrase in HEDGING_PHRASES:
        if phrase in best_para.lower():
            return REFUSAL_TEMPLATE

    return f"[Source: {best_doc}]\n{best_para}"


def main():
    print("Loading policy documents...")
    try:
        docs = retrieve_documents()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    print("Documents loaded. Type your question (or 'exit' to quit).\n")

    while True:
        try:
            question = input("Question: ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue
        answer = answer_question(question, docs)
        print(f"\nAnswer:\n{answer}\n")


if __name__ == "__main__":
    main()