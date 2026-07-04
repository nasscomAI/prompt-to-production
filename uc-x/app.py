import os
import re
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "can", "i", "my", "me", "to", "of", "in", "for", "on", "and", "or",
    "but", "not", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "has", "have", "had", "with", "from", "at",
    "by", "as", "it", "its", "this", "that", "these", "those", "what",
    "when", "where", "who", "how", "which", "why", "if", "then", "else",
    "no", "yes", "am", "have", "has", "had", "do", "does", "did",
    "will", "would", "shall", "should", "may", "might", "can", "could",
    "about", "into", "over", "after", "before", "between", "under",
    "above", "below", "up", "down", "out", "off", "than", "so", "too",
    "very", "just", "also", "more", "any", "each", "every", "both",
    "all", "some", "such", "only", "own", "here", "there",
    "your", "you", "we", "they", "he", "she", "us", "them",
}

ACRONYMS = {"LWP": "Leave Without Pay"}

def retrieve_documents():
    """Load all three policy files and index by subsection number."""
    index = {}
    for doc_name in DOC_NAMES:
        path = os.path.join(DATA_DIR, doc_name)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        index[doc_name] = _parse_subsections(content)
    return index


def _parse_subsections(content):
    """Parse document text into {subsection_number: (subsection_text, section_heading)}."""
    subsections = {}
    lines = content.split("\n")
    i = 0
    current_heading = ""
    while i < len(lines):
        line = lines[i]
        sec_m = re.match(r"^(\d+)\.\s+(.+)$", line)
        if sec_m:
            current_heading = line.strip()
            i += 1
            continue
        sub_m = re.match(r"^(\d+\.\d+)\s+", line)
        if sub_m:
            sub_num = sub_m.group(1)
            sub_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if re.match(r"^\d+\.\d+\s+", next_line):
                    break
                if re.match(r"^\d+\.\s+", next_line):
                    break
                if re.match(r"^═+$", next_line.strip()):
                    i += 1
                    continue
                if next_line.strip():
                    sub_lines.append(next_line)
                i += 1
            text = "\n".join(sub_lines).strip()
            subsections[sub_num] = (text, current_heading)
        else:
            i += 1
    return subsections


def _get_words(text):
    return re.findall(r"[a-z]+", text.lower())


def _expand_acronyms(words):
    expanded = []
    for w in words:
        if w in ACRONYMS:
            expanded.extend(ACRONYMS[w].split())
        else:
            expanded.append(w)
    return expanded


def _word_stems_match(kw, word):
    if kw == word:
        return True
    if len(kw) < 3 or len(word) < 3:
        return False
    if word.startswith(kw) or kw.startswith(word):
        return True
    min_len = min(len(kw), len(word))
    return min_len >= 5 and kw[:5] == word[:5]


def _keyword_matches(keyword, text_words):
    for tw in text_words:
        if _word_stems_match(keyword, tw):
            return True
    return False


def _score_keyword_matches(q_keywords, kw_idf, sub_words):
    score = 0.0
    for kw in q_keywords:
        if _keyword_matches(kw, sub_words):
            score += kw_idf[kw]
    return score


def answer_question(question, index):
    """Search indexed documents and return single-source answer or refusal."""
    q_words = _get_words(question)
    q_words = _expand_acronyms(q_words)
    q_keywords = [w for w in q_words if w not in STOP_WORDS and len(w) >= 2]

    if not q_keywords:
        return REFUSAL_TEMPLATE

    first_action = q_keywords[0]
    section_refs = set(re.findall(r"\b(\d+\.\d+)\b", question))

    all_sections = []
    for doc_name, subsections in index.items():
        for sub_num, (sub_text, heading) in subsections.items():
            search_words = _get_words(sub_text)
            search_words = _expand_acronyms(search_words)
            all_sections.append((doc_name, sub_num, sub_text, heading, search_words))

    total = len(all_sections)

    kw_idf = {}
    for kw in q_keywords:
        count = 0
        for _, _, _, _, sw in all_sections:
            if _keyword_matches(kw, sw):
                count += 1
        kw_idf[kw] = 1.0 + total / (count + 1)

    q_bigrams = set()
    for i in range(len(q_keywords) - 1):
        q_bigrams.add(" ".join(q_keywords[i:i+2]))

    candidates = []

    for doc_name, subsections in index.items():
        for sub_num, (sub_text, heading) in subsections.items():
            search_words = _get_words(sub_text)
            search_words = _expand_acronyms(search_words)

            word_score = _score_keyword_matches(q_keywords, kw_idf, search_words)
            if word_score == 0.0:
                continue

            action_boost = kw_idf[first_action] if _keyword_matches(first_action, search_words) else 0.0

            sub_bigrams = set()
            for i in range(len(search_words) - 1):
                sub_bigrams.add(" ".join(search_words[i:i+2]))
            bigram_score = len(q_bigrams & sub_bigrams) * 5.0

            boost = 25.0 if sub_num in section_refs else 0.0
            score = word_score + action_boost + bigram_score + boost
            display = f"{heading}\n{sub_text}" if heading else sub_text
            candidates.append((score, doc_name, sub_num, display))

    if not candidates:
        return REFUSAL_TEMPLATE

    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score = candidates[0][0]
    top = [c for c in candidates if c[0] == best_score]

    doc_names = set(c[1] for c in top)
    if len(doc_names) > 1:
        return REFUSAL_TEMPLATE

    best = top[0]
    return f"Source: {best[1]}, Section {best[2]}\n\n{best[3]}"


def main():
    print("UC-X \u2014 Ask My Documents")
    print("Loading policy documents...")
    try:
        index = retrieve_documents()
        total = sum(len(v) for v in index.values())
        print(f"Loaded {len(index)} documents, {total} subsections.")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nType your questions below (or 'quit' to exit).\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break

        result = answer_question(question, index)
        print()
        print(result)
        print()


if __name__ == "__main__":
    main()
    