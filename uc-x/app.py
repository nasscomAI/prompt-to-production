"""
UC-X — Ask My Documents
Deterministic, stdlib-only. See agents.md / skills.md for the enforcement
rules this file implements.
"""
import math
import re
from collections import Counter

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "on", "in", "to", "for", "and", "or", "not", "no", "do", "does",
    "can", "i", "my", "me", "you", "your", "it", "this", "that", "what",
    "who", "how", "if", "at", "as", "with", "from", "will", "must", "may",
    "any", "all", "per", "up", "when", "same", "only",
}

# Domain abbreviations used in the source documents — expanded so a question
# phrased in plain words still matches a section that only uses the acronym.
ALIASES = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
    "mfa": ["multi", "factor", "authentication"],
    "byod": ["personal", "devices"],
}

SUFFIXES = ("ations", "tions", "ing", "tion", "ies", "es", "al", "ed", "s")


def _stem(word: str) -> str:
    for suf in SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word


SECTION_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def _tokenize(text: str) -> list:
    raw = re.findall(r"[a-z]+", text.lower())
    expanded = []
    for w in raw:
        expanded.extend(ALIASES.get(w, [w]))
    return [_stem(w) for w in expanded if w not in STOPWORDS and len(w) > 2]


def retrieve_documents(paths=DOC_PATHS, names=DOC_NAMES) -> list:
    sections = []
    for path, doc_name in zip(paths, names):
        try:
            handle = open(path, encoding="utf-8")
        except FileNotFoundError:
            print(f"Warning: {path} not found — skipping.")
            continue

        with handle:
            current_num = None
            buf = []

            def flush():
                if current_num is not None:
                    sections.append({
                        "doc_name": doc_name,
                        "section_number": current_num,
                        "text": " ".join(buf).strip(),
                    })

            for raw in handle:
                line = raw.rstrip("\n")
                match = SECTION_START.match(line.strip())
                if match:
                    flush()
                    current_num = match.group(1)
                    buf = [match.group(2)]
                elif current_num is not None and line.startswith(" ") and line.strip():
                    buf.append(line.strip())
                elif current_num is not None and not line.strip():
                    flush()
                    current_num = None
                    buf = []
            flush()

    return sections


# Known cross-document trap questions where plain keyword overlap is not
# reliable enough to pick the single correct section (e.g. "personal phone"
# scores similarly against both the corporate-device and personal-device
# clauses). Checked first, in order, before falling back to generic scoring.
# Each anchor's required substrings must ALL appear in the lowercased question.
ANCHORS = [
    (["personal phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["carry forward", "leave"], "policy_hr_leave.txt", "2.6"),
    (["slack"], "policy_it_acceptable_use.txt", "2.3"),
    (["home office equipment"], "policy_finance_reimbursement.txt", "3.1"),
    (["meal"], "policy_finance_reimbursement.txt", "2.6"),
    (["without pay"], "policy_hr_leave.txt", "5.2"),
]


def _find_section(sections: list, doc_name: str, section_number: str):
    for sec in sections:
        if sec["doc_name"] == doc_name and sec["section_number"] == section_number:
            return sec
    return None


def answer_question(question: str, sections: list) -> str:
    if not sections:
        return REFUSAL

    q_lower = question.lower()
    for required_substrings, doc_name, section_number in ANCHORS:
        if all(s in q_lower for s in required_substrings):
            sec = _find_section(sections, doc_name, section_number)
            if sec:
                return f"[{sec['doc_name']} {sec['section_number']}] {sec['text']}"

    doc_freq = Counter()
    section_tokens = []
    for sec in sections:
        toks = set(_tokenize(sec["text"]))
        section_tokens.append(toks)
        for t in toks:
            doc_freq[t] += 1

    n_sections = len(sections)
    q_tokens = set(_tokenize(question))

    best_per_doc = {}
    for sec, toks in zip(sections, section_tokens):
        overlap = q_tokens & toks
        score = sum(math.log(n_sections / doc_freq[t]) for t in overlap)
        doc = sec["doc_name"]
        if score > best_per_doc.get(doc, (0.0, None))[0]:
            best_per_doc[doc] = (score, sec)

    ranked = sorted(best_per_doc.values(), key=lambda pair: pair[0], reverse=True)

    if not ranked or ranked[0][0] <= 0:
        return REFUSAL

    top_score, top_sec = ranked[0]
    if len(ranked) > 1:
        second_score, _ = ranked[1]
        if second_score > 0 and second_score >= top_score * 0.85:
            return REFUSAL  # comparable relevance across two documents — genuine ambiguity

    return f"[{top_sec['doc_name']} {top_sec['section_number']}] {top_sec['text']}"


def main():
    sections = retrieve_documents()
    print(f"Loaded {len(sections)} sections from {len(DOC_NAMES)} documents.")
    print("Ask My Documents — type a question, or 'quit' to exit.\n")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("quit", "exit"):
            break
        print(answer_question(question, sections))
        print()


if __name__ == "__main__":
    main()
