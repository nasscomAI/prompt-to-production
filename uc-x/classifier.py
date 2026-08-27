import os
import re
import sys


DOCUMENT_NAMES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def _parse_policy(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    sections = {}
    lines = text.splitlines()
    current_section = None
    section_clauses = []
    pending_clause = None

    def flush_pending():
        nonlocal pending_clause
        if pending_clause is not None:
            section_clauses.append(pending_clause)
            pending_clause = None

    for line in lines:
        stripped = line.strip()
        sep_match = re.match(r"^═+$", stripped)
        section_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)", stripped)

        if sep_match:
            continue
        if section_match:
            flush_pending()
            if current_section and section_clauses:
                sections[current_section] = section_clauses
            current_section = stripped
            section_clauses = []
        elif clause_match:
            flush_pending()
            pending_clause = stripped
        elif pending_clause and stripped:
            pending_clause += " " + stripped
        elif current_section and stripped and not re.match(r"^\d", stripped):
            pass
        elif current_section and stripped:
            section_clauses.append(stripped)

    flush_pending()
    if current_section and section_clauses:
        sections[current_section] = section_clauses

    return sections


def retrieve_documents(filepaths):
    result = {}
    for fp in filepaths:
        fname = os.path.basename(fp)
        if not os.path.exists(fp):
            return {"error": f"File not found: {fname}"}
        try:
            sections = _parse_policy(fp)
        except Exception:
            return {"error": f"Invalid file: {fname}"}
        if not sections:
            return {"error": f"Invalid file: {fname}"}
        result[fname] = sections
    return result


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "have", "has", "had", "can", "will", "would",
    "could", "should", "may", "might", "to", "of", "in", "for", "on",
    "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off",
    "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves", "he", "him",
    "his", "himself", "she", "her", "hers", "herself", "it", "its",
    "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "about", "up", "just", "also", "if", "please", "tell", "me",
}


def _tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _keyword_match_score(question_tokens, clause_text):
    clause_lower = clause_text.lower()
    score = 0
    for token in question_tokens:
        if token in clause_lower:
            score += 1
    return score


DOC_SIGNALS = {
    "policy_hr_leave.txt": [
        "annual leave", "sick leave", "maternity", "paternity",
        "leave encashment", "leave without pay", "lop", "lwp",
        "carry forward", "forfeited", "medical certificate",
        "leave application", "unapproved absence",
    ],
    "policy_it_acceptable_use.txt": [
        "corporate device", "personal device", "byod", "software",
        "install", "password", "email", "internet", "wifi",
        "endpoint security", "mfa", "multi-factor", "remote access",
        "laptop", "smartphone", "mobile phone",
    ],
    "policy_finance_reimbursement.txt": [
        "reimbursement", "allowance", "travel", "d a", "da",
        "daily allowance", "receipt", "home office", "work from home",
        "wfh", "equipment", "mobile phone reimbursement",
        "internet reimbursement", "training", "course fee",
    ],
}


def _rank_documents(question, documents):
    q_lower = question.lower()
    scores = {}
    for doc_name in documents:
        score = 0
        for signal in DOC_SIGNALS.get(doc_name, []):
            if signal in q_lower:
                score += 5
        scores[doc_name] = score
    return scores


def _rank_clauses(question, clauses):
    q_tokens = _tokenize(question)
    if not q_tokens:
        return None, 0

    best_clause = None
    best_score = 0

    RARE_ROOTS = ["install", "slack", "approv", "encash", "forfeit",
                  "receipt", "reimburs", "allow", "certif", "lwp", "lop"]

    for clause in clauses:
        clause_lower = clause.lower()

        stem_score = sum(1 for qt in q_tokens if qt in clause_lower)

        clause_tokens = _tokenize(clause)
        exact_overlap = sum(1 for qt in q_tokens if qt in clause_tokens)

        rare_bonus = 0
        q_lower = question.lower()
        for root in RARE_ROOTS:
            if root in q_lower and root in clause_lower:
                rare_bonus += 3

        phrase_score = 0
        q_words = q_lower.split()
        for i in range(len(q_words) - 1):
            bigram = q_words[i] + " " + q_words[i + 1]
            if bigram in clause_lower:
                phrase_score += 10

        total = stem_score + exact_overlap + rare_bonus + phrase_score
        if total > best_score:
            best_score = total
            best_clause = clause

    return best_clause, best_score


def answer_question(question, documents):
    if isinstance(documents, dict) and "error" in documents:
        return {"error": "Documents not loaded. Run retrieve_documents first."}

    q_tokens = _tokenize(question)
    if not q_tokens:
        return {"answer": REFUSAL_TEMPLATE, "source": None, "section": None, "refused": True}

    doc_scores = _rank_documents(question, documents)
    best_doc = max(doc_scores, key=doc_scores.get)
    best_doc_score = doc_scores[best_doc]

    if best_doc_score == 0:
        return {"answer": REFUSAL_TEMPLATE, "source": None, "section": None, "refused": True}

    sections = documents[best_doc]
    all_clauses = []
    for section_heading, clauses in sections.items():
        for clause in clauses:
            all_clauses.append((section_heading, clause))

    best_section = None
    best_clause = None
    best_score = 0

    for section_heading, clause in all_clauses:
        combined = section_heading + " " + clause
        _, score = _rank_clauses(question, [combined])
        total = score

        if total > best_score:
            best_score = total
            best_section = section_heading
            best_clause = clause

    if best_clause is None or best_score < 1:
        return {"answer": REFUSAL_TEMPLATE, "source": None, "section": None, "refused": True}

    display_name = DOCUMENT_NAMES.get(best_doc, best_doc)
    answer = f"{best_clause}\n\nSource: {display_name} ({best_doc}), Section: {best_section}"
    return {"answer": answer, "source": best_doc, "section": best_section, "refused": False}


def run_cli():
    docs_paths = [
        os.path.join("..", "data", "policy-documents", "policy_hr_leave.txt"),
        os.path.join("..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
        os.path.join("..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
    ]

    print("Loading policy documents...")
    documents = retrieve_documents(docs_paths)
    if isinstance(documents, dict) and "error" in documents:
        print(f"ERROR: {documents['error']}")
        sys.exit(1)

    doc_names = ", ".join(DOCUMENT_NAMES.values())
    print(f"Loaded {len(documents)} documents: {doc_names}")
    print("Type your questions (or 'quit' to exit).\n")

    while True:
        try:
            q = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue

        result = answer_question(q, documents)
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"A: {result['answer']}")
            if result["refused"]:
                print("   (refused)")
            print()
