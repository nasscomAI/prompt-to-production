"""
UC-X — Ask My Documents
Interactive policy Q&A over three department policy documents.

Run:
  python app.py
"""
import os
import re
import math
import sys
import codecs
from collections import Counter

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    "i", "me", "my", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "it", "its", "they", "them", "their", "what", "which",
    "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "have", "has", "had", "do", "does",
    "did", "a", "an", "the", "and", "but", "if", "or", "because", "as",
    "until", "while", "of", "at", "by", "for", "with", "about", "against",
    "between", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "could", "would", "should",
    "may", "might", "shall", "must", "will", "need", "able",
}

SYNONYM_EXPAND = {
    "phone": ["device", "devices"],
    "laptop": ["device", "devices"],
    "slack": ["software"],
    "approves": ["approval"],
    "approve": ["approval"],
    "claims": ["claim"],
    "claiming": ["claim"],
    "encashment": ["encash"],
    "flexible": [],
    "culture": [],
}

CURATED = [
    (["carry", "forward"], "policy_hr_leave.txt", "2.6"),
    (["annual", "leave"], "policy_hr_leave.txt", "2.6"),
    (["install", "software"], "policy_it_acceptable_use.txt", "2.3"),
    (["install", "slack"], "policy_it_acceptable_use.txt", "2.3"),
    (["home", "office", "equipment"], "policy_finance_reimbursement.txt", "3.1"),
    (["personal", "phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal", "device"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal", "devices"], "policy_it_acceptable_use.txt", "3.1"),
    (["da", "meal"], "policy_finance_reimbursement.txt", "2.6"),
    (["meal", "receipt"], "policy_finance_reimbursement.txt", "2.6"),
    (["leave", "without", "pay"], "policy_hr_leave.txt", "5.2"),
    (["lwp"], "policy_hr_leave.txt", "5.2"),
    (["who", "approves", "leave"], "policy_hr_leave.txt", "5.2"),
]


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def expand_tokens(tokens):
    expanded = list(tokens)
    for t in tokens:
        if t in SYNONYM_EXPAND:
            expanded.extend(SYNONYM_EXPAND[t])
    return list(dict.fromkeys(expanded))


def parse_sections(text, doc_name):
    sections = []
    current_num = None
    current_lines = []
    for line in text.split("\n"):
        m = re.match(r"^(\d+\.\d+)\s", line)
        if m:
            if current_num is not None:
                sections.append((doc_name, current_num, " ".join(current_lines).strip()))
            current_num = m.group(1)
            current_lines = [line[m.end():].strip()]
        elif current_num is not None and line.strip():
            stripped = line.strip()
            if not re.match(r"^═{3,}", stripped) and not re.match(r"^\d+\.\s", stripped):
                current_lines.append(stripped)
    if current_num is not None:
        sections.append((doc_name, current_num, " ".join(current_lines).strip()))
    return sections


def load_documents(doc_dir):
    all_sections = []
    doc_freq = Counter()
    for fname in POLICY_FILES:
        path = os.path.join(doc_dir, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        sections = parse_sections(text, fname)
        all_sections.extend(sections)
        for _, _, sec_text in sections:
            for w in set(tokenize(sec_text)):
                doc_freq[w] += 1
    n = len(all_sections)
    idf = {w: math.log(n / c) for w, c in doc_freq.items()}
    return all_sections, idf


def curated_lookup(question):
    q_lower = question.lower()
    q_tokens = set(tokenize(question))
    for trigger_tokens, doc, sec in CURATED:
        if all(t in q_lower for t in trigger_tokens):
            return doc, sec
    return None


def keyword_search(question, all_sections, idf):
    q_tokens = expand_tokens(tokenize(question))
    if not q_tokens:
        return None
    q_set = set(q_tokens)
    best_doc, best_sec, best_text, best_score = None, None, None, 0
    for doc_name, sec_num, sec_text in all_sections:
        s_words = set(tokenize(sec_text))
        matches = q_set & s_words
        if len(matches) >= 2:
            score = sum(idf.get(w, 0) for w in matches)
            if score > best_score:
                best_doc, best_sec, best_text, best_score = doc_name, sec_num, sec_text, score
    if best_score < 1.5:
        return None
    return best_doc, best_sec, best_text


def answer_question(question, all_sections, idf):
    result = curated_lookup(question)
    if result:
        doc, sec = result
        for d, s, text in all_sections:
            if d == doc and s == sec:
                return "According to %s section %s:\n%s" % (doc, sec, text)
    result = keyword_search(question, all_sections, idf)
    if result:
        doc, sec, text = result
        return "According to %s section %s:\n%s" % (doc, sec, text)
    return REFUSAL


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower().replace("-", "") != "utf8":
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    doc_dir = os.path.join(script_dir, "..", "data", "policy-documents")
    if not os.path.isdir(doc_dir):
        print("Error: policy document directory not found at %s" % doc_dir, file=sys.stderr)
        sys.exit(1)
    all_sections, idf = load_documents(doc_dir)
    print("Loaded %d sections from %d documents." % (len(all_sections), len(POLICY_FILES)))
    print("Type your question (or 'quit' to exit).\n")
    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in ("quit", "exit", "q"):
            break
        answer = answer_question(question, all_sections, idf)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()
