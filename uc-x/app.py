"""
UC-X — Ask My Documents
Interactive CLI that answers CMC employee policy questions.
Answers come from exactly one document section with citation,
or the refusal template if the question is not covered.
"""
import os
import re
import sys


DOCUMENT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "({}).\n"
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "to", "of", "in", "for", "on", "with", "at",
    "from", "by", "about", "as", "into", "through", "during", "before",
    "after", "above", "below", "between", "out", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "just", "because", "but", "and", "or",
    "if", "while", "what", "which", "who", "whom", "this", "that", "these",
    "those", "it", "its", "i", "me", "we", "us", "you", "he", "she", "they",
    "them", "my", "your", "his", "her", "their", "our", "can", "could",
    "itself", "myself",
    "yourself", "himself", "herself", "itself", "ourselves", "yourselves",
    "themselves",
}


def retrieve_documents():
    indexed = {}
    for rel_path in DOCUMENT_PATHS:
        path = os.path.join(os.path.dirname(__file__), rel_path)
        filename = os.path.basename(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        indexed[filename] = _parse_subsections(text)
    return indexed


def _parse_subsections(text):
    lines = text.splitlines()

    sections = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("\u2550"):
            i += 1
            continue

        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            break
        heading = lines[j].strip()

        k = j + 1
        while k < len(lines) and not lines[k].startswith("\u2550"):
            k += 1
        if k >= len(lines):
            break

        content_start = k + 1
        content_end = content_start
        while content_end < len(lines) and not lines[content_end].startswith("\u2550"):
            content_end += 1

        sections.append({
            "heading": heading,
            "content_start": content_start,
            "content_end": content_end,
        })

        i = content_end

    result = []
    for section in sections:
        heading = section["heading"]
        major_match = re.match(r"^(\d+)\.\s", heading)
        major_num = major_match.group(1) if major_match else None

        content_lines = [
            lines[idx].strip()
            for idx in range(section["content_start"], section["content_end"])
            if lines[idx].strip()
        ]

        current_sub = None
        current_sub_lines = []

        for line in content_lines:
            sub_match = re.match(r"^(\d+)\.(\d+)\s", line)
            if sub_match and sub_match.group(1) == major_num:
                if current_sub is not None:
                    result.append({
                        "section_number": current_sub,
                        "heading": heading,
                        "content": current_sub_lines,
                    })
                current_sub = sub_match.group(0).strip()
                current_sub_lines = [line]
            elif current_sub is not None:
                current_sub_lines.append(line)

        if current_sub is not None:
            result.append({
                "section_number": current_sub,
                "heading": heading,
                "content": current_sub_lines,
            })

    return result


def _get_keywords(text):
    words = set()
    for word in text.split():
        word = word.strip(".,;:!?\"'()[]{}")
        if word and word.lower() not in STOP_WORDS and len(word) >= 2:
            words.add(word.lower())
    return words


def _get_all_words(text):
    words = []
    for word in text.split():
        word = word.strip(".,;:!?\"'()[]{}")
        if word:
            words.append(word.lower())
    return words


def _keyword_prefix_match(question_word, text_words):
    """Check if question_word matches any text word using 4-char prefix
    matching (for words >= 4 chars) or exact matching (for words < 4 chars)."""
    if len(question_word) < 4:
        return question_word in text_words
    prefix = question_word[:4]
    return any(w.startswith(prefix) for w in text_words)


def answer_question(question, indexed_documents):
    q_keywords = _get_keywords(question)
    if not q_keywords:
        return _refusal()

    # Phase 1 — Cross-document detection using CONTENT-ONLY exact matching.
    # This avoids false positives from heading words (e.g. "WORK" in
    # section-3 headings of finance documents).
    scored_content = []
    for doc_name, sections in indexed_documents.items():
        for section in sections:
            content_text = " ".join(section["content"])
            content_keywords = _get_keywords(content_text)
            overlap = q_keywords & content_keywords
            if overlap:
                scored_content.append({
                    "kw_score": len(overlap),
                    "doc_name": doc_name,
                    "section": section,
                })

    if not scored_content:
        return _refusal()

    best_kw = max(s["kw_score"] for s in scored_content)

    top_by_doc = {}
    for s in scored_content:
        if s["kw_score"] >= best_kw:
            top_by_doc.setdefault(s["doc_name"], []).append(s)

    if len(top_by_doc) == 1:
        best_doc = list(top_by_doc.keys())[0]
    else:
        doc_counts = {d: len(secs) for d, secs in top_by_doc.items()}
        max_count = max(doc_counts.values())
        docs_with_max = [d for d, c in doc_counts.items() if c >= max_count]
        if len(docs_with_max) > 1:
            return _refusal()
        best_doc = docs_with_max[0]

    # Phase 2 — Within the winning document, re-score ALL sections using
    # heading + content with prefix matching, plus subsection tiebreaker.
    def _sub_sort_key(section):
        parts = section["section_number"].split(".")
        return (int(parts[0]), int(parts[1]))

    def _content_prefix_count(section, keywords):
        content_text = " ".join(section["content"])
        content_words = _get_all_words(content_text)
        count = 0
        for kw in keywords:
            if len(kw) < 4:
                count += content_words.count(kw.lower())
            else:
                prefix = kw[:4]
                count += sum(1 for w in content_words if w.startswith(prefix))
        return count

    best_section = None
    best_score = (-1, -1, -1, -1, -1)  # (prefix, heading, content_prefix, sub_major, sub_minor)

    for section in indexed_documents[best_doc]:
        heading_text = section["heading"]
        content_text = " ".join(section["content"])
        heading_words = set(_get_all_words(heading_text))
        content_words_set = set(_get_all_words(content_text))
        text_words = heading_words | content_words_set

        prefix_count = sum(
            1 for kw in q_keywords
            if _keyword_prefix_match(kw, text_words)
        )
        heading_count = sum(
            1 for kw in q_keywords
            if _keyword_prefix_match(kw, heading_words)
        )
        content_pfx_count = _content_prefix_count(section, q_keywords)
        sub_key = _sub_sort_key(section)

        score = (prefix_count, heading_count, content_pfx_count, sub_key[0], sub_key[1])
        if score > best_score:
            best_score = score
            best_section = section

    content_text = "\n".join(best_section["content"])
    return (
        f"{content_text}\n\n"
        f"(Source: {best_doc}, section {best_section['section_number']})"
    )


def _refusal():
    filenames = ", ".join(os.path.basename(p) for p in DOCUMENT_PATHS)
    return REFUSAL_TEMPLATE.format(filenames)


def main():
    print("UC-X \u2014 Ask My Documents")
    print("Type your question or 'quit' to exit.\n")

    try:
        indexed = retrieve_documents()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

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

        answer = answer_question(question, indexed)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
