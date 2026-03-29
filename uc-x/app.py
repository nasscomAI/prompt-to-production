"""
UC-X: Ask My Documents — Policy Q&A CLI App
Strict rules:
  1. Answer from ONE document only — no cross-document blending
  2. Cite document name + section number for every answer
  3. If answer not found in ANY document → use exact refusal template
  4. NEVER use hedging phrases like "while not explicitly covered", "typically", "generally"
"""

import os
import re
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
BASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
POLICY_FILES = {
    "policy_hr_leave.txt":              os.path.join(BASE, "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt":     os.path.join(BASE, "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(BASE, "policy_finance_reimbursement.txt"),
}

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)

# Domain keyword boosting — steers retrieval to the correct document
# when surface keywords overlap across docs (e.g. "laptop" appears in Finance and IT docs)
DOMAIN_BOOSTS = {
    "policy_hr_leave.txt": [
        "leave", "annual leave", "sick leave", "maternity", "paternity", "lwp",
        "carry forward", "carry-forward", "absence", "public holiday", "grievance",
        "encashment", "lop", "without pay", "loss of pay",
    ],
    "policy_it_acceptable_use.txt": [
        "software", "install", "laptop", "work laptop", "corporate device",
        "byod", "personal device", "personal phone", "mobile phone",
        "password", "email", "internet", "network", "wifi",
        "it department", "security", "access control", "system",
        "slack", "app", "application", "work files", "endpoint",
    ],
    "policy_finance_reimbursement.txt": [
        "reimburse", "reimbursement", "expense", "allowance", "claim",
        "travel", "hotel", "da", "daily allowance", "meal", "receipt",
        "home office", "equipment allowance", "training", "mobile reimbursement",
        "internet reimbursement", "wfh", "work from home",
    ],
}


# ── Document loading ────────────────────────────────────────────────────────
def load_documents():
    docs = {}
    for name, path in POLICY_FILES.items():
        with open(path, 'r', encoding='utf-8') as f:
            docs[name] = f.read()
    return docs


def parse_sections(text):
    """Split document into sections by numbered headings (e.g. '2. ANNUAL LEAVE')."""
    sections = []
    current_heading = "PREAMBLE"
    current_lines = []
    for line in text.splitlines():
        m = re.match(r'^(\d+(?:\.\d+)?)\s+[A-Z]', line.strip())
        if m:
            if current_lines:
                sections.append((current_heading, '\n'.join(current_lines)))
            current_heading = line.strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_heading, '\n'.join(current_lines)))
    return sections


# ── Retrieval ───────────────────────────────────────────────────────────────
def compute_domain_bonus(question_lower, doc_name):
    """Return bonus score: 3 points per domain keyword hit in question."""
    return sum(3 for kw in DOMAIN_BOOSTS.get(doc_name, []) if kw in question_lower)


def find_relevant_sections(question, docs):
    """
    For each document, find its best-matching section + domain bonus.
    Returns one result per document, sorted by total score descending.
    Domain bonus prevents cross-topic retrieval errors (e.g. Finance→laptop).
    """
    stopwords = {'the','a','an','is','in','on','at','to','for','of','and','or',
                 'my','i','can','what','who','how','when','does','do','be','with',
                 'are','was','were','not','it','this','that','will','from','have'}
    query_words = set(re.findall(r'\b\w+\b', question.lower())) - stopwords
    question_lower = question.lower()

    results = []
    for doc_name, doc_text in docs.items():
        domain_bonus = compute_domain_bonus(question_lower, doc_name)
        sections = parse_sections(doc_text)
        # Pick the best section from this document
        best_score, best_heading, best_content = 0, None, None
        for heading, content in sections:
            content_words = set(re.findall(r'\b\w+\b', content.lower()))
            raw_score = len(query_words & content_words)
            total = raw_score + domain_bonus
            if total > best_score:
                best_score = total
                best_heading = heading
                best_content = content
        if best_score > 0 and best_content:
            results.append((doc_name, best_heading, best_content, best_score))

    results.sort(key=lambda x: -x[3])
    return results


def answer_question(question, docs):
    """
    Returns (answer_text, source_doc, section_heading) or refusal.
    Single-source rule enforced. Cross-document ambiguity → refusal.
    """
    hits = find_relevant_sections(question, docs)
    if not hits:
        return REFUSAL, None, None

    best_doc, best_heading, best_content, best_score = hits[0]

    # Cross-document ambiguity: second doc from different source with close score → refuse
    if len(hits) > 1:
        second_doc, _, _, second_score = hits[1]
        if second_doc != best_doc and second_score >= best_score * 0.8:
            return REFUSAL, None, None

    lines = [l.strip() for l in best_content.splitlines() if l.strip()]
    answer = '\n'.join(lines[:12])
    return answer, best_doc, best_heading


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("UC-X: Ask My Documents — Policy Q&A")
    print("Docs: HR Leave | IT Acceptable Use | Finance Reimbursement")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    docs = load_documents()
    print(f"Loaded {len(docs)} policy documents.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ('quit', 'exit'):
            print("Goodbye.")
            break

        answer, source_doc, section = answer_question(question, docs)

        print("\n" + "-" * 60)
        if source_doc:
            print(f"Answer:\n{answer}")
            print(f"\nSource: {source_doc} — {section}")
        else:
            print(f"Answer:\n{answer}")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
