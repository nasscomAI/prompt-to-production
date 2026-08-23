"""
UC-X — Ask My Documents
Interactive CLI that answers employee questions about company policy
by reading from exactly three policy documents. Never blends across
documents, never hedges, always cites sources.
"""
import argparse
import logging
import math
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

STOP_WORDS = {
    "a", "an", "the", "is", "it", "at", "on", "in", "to", "for", "of",
    "with", "and", "or", "from", "by", "can", "i", "my", "what", "do",
    "does", "be", "not", "this", "that", "are", "was", "were", "been",
    "have", "has", "had", "may", "will", "would", "could", "should",
    "shall", "about", "into", "through", "during", "before", "after",
    "above", "below", "between", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "no", "nor", "only", "own", "so",
    "than", "too", "very", "just", "because", "as", "until", "while",
    "who", "whom", "which", "if", "but", "up", "down",
}

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("uc-x")


def retrieve_documents(file_paths):
    """Load all policy files and index by document name and section number.

    Returns dict: {doc_name: {section_number: section_content}}
    """
    index = {}
    for fp in file_paths:
        doc_name = os.path.basename(fp)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
        except (FileNotFoundError, IOError) as e:
            logger.error("Could not read %s: %s", fp, e)
            continue

        sections = _parse_sections(text)
        index[doc_name] = sections
    return index


def _parse_sections(text):
    """Parse policy text into {section_number: section_content}.

    Each subsection includes its top-level section header for context.
    """
    sections = {}
    lines = text.splitlines()
    current_section = None
    current_lines = []
    current_header = ""

    section_re = re.compile(r"^(\d+\.\d+)\s")
    header_re = re.compile(r"^(\d)\.\s+([A-Z].+)")

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("═"):
            continue

        hm = header_re.match(line_stripped)
        if hm:
            if current_section is not None:
                sections[current_section] = (
                    current_header,
                    "\n".join(current_lines).strip(),
                )
            current_header = line_stripped
            current_section = None
            current_lines = []
            continue

        m = section_re.match(line_stripped)
        if m:
            if current_section is not None:
                sections[current_section] = (
                    current_header,
                    "\n".join(current_lines).strip(),
                )
            current_section = m.group(1)
            current_lines = [line_stripped]
        else:
            if current_section is not None:
                current_lines.append(line_stripped)

    if current_section is not None:
        sections[current_section] = (
            current_header,
            "\n".join(current_lines).strip(),
        )

    return sections


def _extract_keywords(question):
    """Extract meaningful keywords from a question, removing stop words and punctuation."""
    words = re.sub(r"[^a-z0-9\s]", "", question.lower()).split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def _compute_idf(index):
    """Compute inverse document frequency for each word across all sections."""
    word_doc_count = {}
    total_sections = 0
    for doc_name, sections in index.items():
        for sec_num, (header, content) in sections.items():
            total_sections += 1
            words = set((header + " " + content).lower().split())
            for w in words:
                word_doc_count[w] = word_doc_count.get(w, 0) + 1
    idf = {}
    for w, count in word_doc_count.items():
        idf[w] = math.log(total_sections / (1 + count))
    return idf


def _keyword_in_text(kw, text):
    """Check if a keyword appears in the text, handling common morphological variants.
    
    For short keywords (<=3 chars), requires exact word match.
    For longer keywords, checks if any word in the text shares a common prefix
    of at least 5 characters with the keyword.
    This handles plurals ('phone'/'phones'), different forms ('approval'/'approves'), etc.
    """
    if len(kw) <= 3:
        return re.search(r"\b" + re.escape(kw) + r"\b", text) is not None
    prefix = kw[:5]
    return re.search(r"\b" + re.escape(prefix), text) is not None


def _keyword_df(keyword, index):
    """Count how many sections contain the keyword (document frequency)."""
    count = 0
    for doc_name, sections in index.items():
        for sec_num, (header, content) in sections.items():
            text = (header + " " + content).lower()
            if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                count += 1
    return count


def _score_section(keywords, header, content, idf):
    """Return a relevance score for a section given question keywords.

    Header matches are weighted 3x, content matches 1x.
    """
    header_lower = header.lower()
    content_lower = content.lower()
    score = 0.0
    matched = 0
    for kw in keywords:
        in_header = _keyword_in_text(kw, header_lower)
        in_content = _keyword_in_text(kw, content_lower)
        if in_header or in_content:
            matched += 1
            weight = 3 if in_header else 1
            score += idf.get(kw, 1.0) * weight
    return score, matched


def answer_question(question, index, idf):
    """Search indexed documents for a relevant section.

    Returns a single-source answer with citation, or the refusal template.
    """
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    keywords = _extract_keywords(question)
    if not keywords:
        return REFUSAL_TEMPLATE

    best_doc = None
    best_section = None
    best_score = 0.0
    best_matched = 0

    for doc_name, sections in index.items():
        doc_best_sec = None
        doc_best_score = 0.0
        doc_best_matched = 0
        for sec_num, (header, content) in sections.items():
            score, matched = _score_section(keywords, header, content, idf)
            if matched > doc_best_matched or (matched == doc_best_matched and score > doc_best_score):
                doc_best_matched = matched
                doc_best_score = score
                doc_best_sec = sec_num
        if doc_best_sec is not None and (doc_best_matched > best_matched or (doc_best_matched == best_matched and doc_best_score > best_score)):
            best_matched = doc_best_matched
            best_score = doc_best_score
            best_doc = doc_name
            best_section = doc_best_sec

    if best_doc is None or best_matched < 1:
        return REFUSAL_TEMPLATE

    if best_matched < 2 and best_score < 3.0:
        return REFUSAL_TEMPLATE

    header, content = index[best_doc][best_section]
    return f"{header}\n{content}\n\nSource: {best_doc}, section {best_section}"


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument(
        "--policy-dir",
        default=POLICY_DIR,
        help="Directory containing policy text files",
    )
    args = parser.parse_args()

    file_paths = [
        os.path.join(args.policy_dir, fname) for fname in POLICY_FILES
    ]

    index = retrieve_documents(file_paths)
    if not index:
        print("Error: No policy documents could be loaded.", file=sys.stderr)
        sys.exit(1)

    idf = _compute_idf(index)

    print("UC-X — Ask My Documents (type 'quit' to exit)")
    print("-" * 50)

    for line in sys.stdin:
        question = line.strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        answer = answer_question(question, index, idf)
        print(answer)
        print()


if __name__ == "__main__":
    main()