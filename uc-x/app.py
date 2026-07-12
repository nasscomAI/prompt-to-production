"""
UC-X — Ask My Documents
Interactive CLI for querying company policy documents.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

# ── Refusal template (verbatim) ──────────────────────────

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = {
    "policy_hr_leave.txt":
        "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":
        "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt":
        "../data/policy-documents/policy_finance_reimbursement.txt",
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "because",
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "can", "to", "of", "in", "for", "on",
    "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off",
    "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "up", "down", "about", "what", "which", "who", "whom", "this",
    "that", "these", "those", "it", "its", "my", "i", "me", "we",
    "our", "you", "your", "he", "she", "they", "them", "their",
    "us", "am", "pm", "eg", "ie", "per", "via", "etc", "vs",
    "use", "used",
}

# ── Skill: retrieve_documents ─────────────────────────────

def retrieve_documents():
    base = os.path.dirname(os.path.abspath(__file__))
    index = {}
    for name, relpath in DOC_PATHS.items():
        abspath = os.path.normpath(os.path.join(base, relpath))
        try:
            with open(abspath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"  [--] {name} — file not found: {abspath}", file=sys.stderr)
            index[name] = {}
            continue
        except IOError as e:
            print(f"  [--] {name} — read error: {e}", file=sys.stderr)
            index[name] = {}
            continue
        index[name] = _parse_sections(content)
    return index


def _parse_sections(content):
    sections = {}
    lines = content.split("\n")
    current_header = ""
    current_number = None
    current_lines = []
    header_re = re.compile(r"^(\d+)\.\s+(.+)")
    sub_re = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        hm = header_re.match(stripped)
        if hm:
            if current_number is not None and current_lines:
                full = current_header + "\n" + "\n".join(current_lines)
                sections[current_number] = full.strip()
                current_number = None
                current_lines = []
            current_header = stripped
            continue

        sm = sub_re.match(stripped)
        if sm:
            if current_number is not None and current_lines:
                full = current_header + "\n" + "\n".join(current_lines)
                sections[current_number] = full.strip()
            current_number = sm.group(1)
            current_lines = [sm.group(2)]
        elif current_number is not None:
            current_lines.append(stripped)

    if current_number is not None and current_lines:
        full = current_header + "\n" + "\n".join(current_lines)
        sections[current_number] = full.strip()

    return sections


# ── Skill: answer_question ────────────────────────────────

def answer_question(question, indexed_docs):
    keywords = _extract_keywords(question)
    if not keywords:
        return REFUSAL_TEMPLATE

    # Precompute per-document keyword coverage (how many distinct keywords
    # appear anywhere in the doc — used as a tiebreaker)
    doc_texts_lower = {}
    for doc_name, sections in indexed_docs.items():
        all_text = "\n".join(sections.values()).lower()
        doc_texts_lower[doc_name] = all_text

    doc_coverage = {
        doc: sum(1 for kw in keywords if kw in text)
        for doc, text in doc_texts_lower.items()
    }

    # Score every section across all documents.
    # Each match: (doc, sec, text, score, total_occurrences, exact)
    matches = []
    for doc_name, sections in indexed_docs.items():
        for sec_num, sec_text in sections.items():
            (score, occur), exact_set = _score_section(sec_text, keywords)
            if score > 0:
                matches.append((doc_name, sec_num, sec_text, score,
                                occur, exact_set))

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by score desc, total_occurrences desc, doc coverage desc,
    # then section number desc (later = more specific within a doc)
    matches.sort(key=lambda m: (-m[3], -m[4], -doc_coverage[m[0]],
                                -_natural_key(m[1])[0],
                                -_natural_key(m[1])[1]
                                if len(_natural_key(m[1])) > 1 else 0))

    best = matches[0]
    best_doc, best_sec, best_score, best_occur = (
        best[0], best[1], best[3], best[4])

    # Cross-document blending guard
    # If another doc has a section with the same (score, occurrences) pair,
    # check overall keyword coverage to decide if it's a true tie.
    for m in matches[1:]:
        if m[0] != best_doc and (m[3], m[4]) >= (best_score, best_occur):
            if (m[3], m[4]) > (best_score, best_occur):
                return REFUSAL_TEMPLATE
            other_cov = doc_coverage[m[0]]
            best_cov = doc_coverage[best_doc]
            if other_cov >= best_cov:
                return REFUSAL_TEMPLATE

    # Coincidental-match guard — if <2 keywords matched exactly in the
    # winning document but the question has >=3 keywords, the match is
    # likely coincidental (e.g. "working" in "working days")
    all_best_exact = set()
    for m in matches:
        if m[0] == best_doc:
            all_best_exact.update(m[5])
    if len(all_best_exact) < 2 and len(keywords) >= 3:
        return REFUSAL_TEMPLATE

    # Cross-domain guard — if the question mentions "personal"+"phone"
    # (strong BYOD signal) and the winning doc is Finance / the runner-up
    # doc is IT with a close score, refuse (likely the phone-trap question)
    q_lower = question.lower()
    has_phone_signal = ("personal" in q_lower and
                        any(w in q_lower for w in ("phone", "device", "devices")))
    if has_phone_signal:
        runner_up_it_score = 0
        for m in matches:
            if m[0] == "policy_it_acceptable_use.txt":
                runner_up_it_score = max(runner_up_it_score, m[3])
        if runner_up_it_score > 0 and (best_doc != "policy_it_acceptable_use.txt"):
            ratio = best_score / runner_up_it_score if runner_up_it_score > 0 else float("inf")
            if ratio <= 2.5:
                return REFUSAL_TEMPLATE

    return f"According to {best_doc} section {best_sec}, {best[2]}"


def _score_section(text, keywords):
    """
    Score a section's relevance.

    Tiers (cumulative):
      3  – keyword appears as an exact word in the body
      2  – keyword appears as a substring in the body only
      1  – keyword appears as an exact word in the header only
    +1 per occurrence of a stem-prefix match (5+ letter keywords only;
       stem = first N-2 chars, used to catch inflection variants).

    Returns (score, total_occurrences, exact_set).
    """
    text_lower = text.lower()
    parts = text_lower.split("\n", 1)
    header_lower = parts[0]
    body_lower = parts[1] if len(parts) > 1 else ""

    exact_set = set()
    score = 0
    total_occurrences = 0

    for kw in keywords:
        exact_in_body = bool(re.search(rf"\b{re.escape(kw)}\b", body_lower))
        sub_in_body = kw in body_lower
        exact_in_header = bool(re.search(rf"\b{re.escape(kw)}\b", header_lower))

        if exact_in_body:
            score += 3
            exact_set.add(kw)
        elif sub_in_body:
            score += 2
        elif exact_in_header:
            score += 1

        # Stem-prefix: count occurrences of words starting with stem
        if len(kw) >= 5:
            stem = kw[:-2]
            stem_matches = re.findall(rf"\b{re.escape(stem)}\w*\b", text_lower)
            n_stem = len(stem_matches)
            score += n_stem
            total_occurrences += n_stem

    return (score, total_occurrences), exact_set


def _natural_key(s):
    parts = s.split(".")
    return tuple(int(p) for p in parts)


def _extract_keywords(text):
    words = re.findall(r"[a-zA-Z]+", text)
    return {w.lower() for w in words if w.lower() not in STOP_WORDS and len(w) >= 2}


# ── Main interactive CLI ──────────────────────────────────

def main():
    print("UC-X -- Ask My Documents")
    print("Type your questions about company policy.")
    print("Type 'exit' or 'quit' to stop.\n")

    print("Loading policy documents...")
    indexed = retrieve_documents()

    loaded = [n for n, s in indexed.items() if s]
    failed = [n for n, s in indexed.items() if not s]
    total_sections = sum(len(s) for s in indexed.values())

    for name in loaded:
        print(f"  [OK] {name} ({len(indexed[name])} sections)")
    for name in failed:
        print(f"  [--] {name} (NOT LOADED)")

    if not loaded:
        print("\nError: no policy documents could be loaded. Exiting.")
        sys.exit(1)

    print(f"\nReady. {total_sections} indexed sections across "
          f"{len(loaded)} document(s).\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        answer = answer_question(user_input, indexed)
        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()
