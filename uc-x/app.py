import argparse
import re
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_MESSAGE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt,\n"
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOPWORDS = frozenset({
    "a", "an", "the", "can", "i", "my", "me", "on", "to", "is", "it", "in",
    "for", "of", "and", "or", "be", "are", "was", "were", "do", "does", "did",
    "has", "have", "had", "not", "no", "but", "if", "so", "we", "you", "he",
    "she", "they", "him", "her", "us", "them", "this", "that", "these", "those",
    "am", "been", "being", "having", "doing", "get", "got", "use", "used",
    "using", "about", "into", "over", "after", "before", "between", "out", "up",
    "down", "at", "by", "as", "with", "from", "all", "each", "every", "some",
    "any", "what", "when", "where", "who", "which", "how", "why", "please",
    "would", "could", "should", "may", "might", "must", "shall", "will",
    "working", "work", "company", "view", "within", "via", "per",
})


def sanitize(text):
    return text.replace("═", "-")


def load_documents():
    index = {}
    for filename in DOCUMENTS:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Policy file not found: {filepath}")
        content = filepath.read_text(encoding="utf-8")
        sections = parse_sections(content)
        doc_tokens = re.findall(r"[a-zA-Z]+", filename.replace(".txt", "").replace("policy_", ""))
        for sec_num, sec_title, sec_lines in sections:
            sec_lines.insert(0, " ".join(doc_tokens))
        index[filename] = sections
    return index


def parse_sections(content):
    sections = []
    lines = content.splitlines()
    current_sec = None
    current_lines = []
    section_header = None

    for raw in lines:
        line = raw.strip()
        if not line or re.match(r"^[═\-\s]+$", line):
            continue
        m_sub = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
        m_sec = re.match(r"^(\d+)\.\s+(.+)$", line)
        if m_sub:
            if current_sec is not None:
                sections.append((current_sec[0], current_sec[1], current_lines))
            current_sec = (m_sub.group(1), m_sub.group(2))
            current_lines = [line]
            if section_header:
                current_lines.insert(0, section_header)
        elif m_sec:
            section_header = line
            if current_sec is not None:
                sections.append((current_sec[0], current_sec[1], current_lines))
                current_sec = None
                current_lines = []
        elif current_sec is not None:
            current_lines.append(line)

    if current_sec is not None:
        sections.append((current_sec[0], current_sec[1], current_lines))

    return sections


def tokenize(text):
    return [w for w in re.findall(r"[a-zA-Z]\w*", text.lower()) if w not in STOPWORDS]

def stem(word):
    for suf in ["'s", "es", "ed", "ing", "er", "est", "ly", "al", "tion", "ment"]:
        if word.endswith(suf) and len(word) > len(suf) + 2:
            return word[:-len(suf)]
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word


def compute_idf(index):
    doc_count = sum(len(sections) for sections in index.values())
    word_docs = Counter()
    for sections in index.values():
        seen = set()
        for _, _, lines in sections:
            text = " ".join(lines).lower()
            for w in tokenize(text):
                seen.add(w)
        for w in seen:
            word_docs[w] += 1
    inv = {}
    for w, c in word_docs.items():
        inv[w] = doc_count / max(c, 1)
    return inv


def build_doc_vocab(index):
    doc_vocab = {}
    for doc_name, sections in index.items():
        all_words = set()
        for _, _, lines in sections:
            for w in tokenize(" ".join(lines)):
                all_words.add(w)
        doc_vocab[doc_name] = all_words
    return doc_vocab


PERSONAL_PHONE_TRIGGERS = ["personal phone", "personal device", "personal laptop",
                           "personal computer", "personal mobile"]


def _match_personal_phone(question):
    q = question.lower()
    for phrase in PERSONAL_PHONE_TRIGGERS:
        if phrase in q and ("access" in q or "work file" in q or "work from home" in q):
            return True
    return False


def search_index(index, idf, doc_vocab, question):
    q_words = tokenize(question)
    if not q_words:
        return None
    q_stems = {w: stem(w) for w in q_words}

    # Enforce agents.md rule: personal-phone question => IT policy only
    if _match_personal_phone(question):
        filtered = {k: v for k, v in index.items() if "it_acceptable_use" in k}
        return _search_in(filtered, idf, doc_vocab, q_words, q_stems)

    return _search_in(index, idf, doc_vocab, q_words, q_stems)


def _search_in(index, idf, doc_vocab, q_words, q_stems):
    doc_coverage = {}
    for doc_name, vocab in doc_vocab.items():
        covered = sum(1 for w in q_words if w in vocab or stem(w) in {stem(v) for v in vocab})
        doc_coverage[doc_name] = covered / len(q_words)

    candidates = []
    for doc_name, sections in index.items():
        dc_bonus = 1.0 + 2.0 * doc_coverage.get(doc_name, 0)
        for sec_num, sec_title, sec_lines in sections:
            flat = " ".join(sec_lines).lower()
            sec_tokens = tokenize(flat)
            sec_words = set(sec_tokens)
            sec_stems = {stem(w) for w in sec_tokens}
            matches = []
            for qw in q_words:
                if qw in sec_words or q_stems[qw] in sec_stems:
                    matches.append(qw)
            if not matches:
                continue
            raw_score = sum(idf.get(w, 1.0) for w in matches)
            proportion = len(matches) / len(q_words)
            score = raw_score * proportion * dc_bonus
            if raw_score < 3.0:
                continue
            candidates.append((score, doc_name, sec_num, sec_title, sec_lines))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[0])
    score, doc_name, sec_num, sec_title, sec_lines = candidates[0]
    body = " ".join(sec_lines)
    body = sanitize(body)
    return f"{doc_name} section {sec_num}:\n{body}"


def answer_question(index, idf, doc_vocab, question):
    result = search_index(index, idf, doc_vocab, question)
    if result:
        return result
    return REFUSAL_MESSAGE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", "-q", help="Single question mode")
    args = parser.parse_args()

    index = load_documents()
    idf = compute_idf(index)
    doc_vocab = build_doc_vocab(index)

    if args.question:
        print(answer_question(index, idf, doc_vocab, args.question))
        return

    print("UC-X - Ask My Documents")
    print("Type your question or 'quit' to exit.")
    print("-" * 50)
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue
        print()
        print(answer_question(index, idf, doc_vocab, q))
        print()


if __name__ == "__main__":
    main()
