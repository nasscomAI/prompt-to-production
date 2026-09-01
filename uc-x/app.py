"""
UC-X Policy QA Agent — Interactive CLI for company policy questions.
Implements retrieve_documents and answer_question skills.

Retrieval design:
- Documents are parsed into sections keyed by section number, each with
  its parent heading (e.g., section 3.1 under "PERSONAL DEVICES (BYOD)").
- Questions are decomposed into concepts (multi-word policy terms such as
  "leave without pay"), remaining keywords, and phrase n-grams.
- The single best-matching section is returned with a citation. A question
  must align with at least two distinct signals or it is refused verbatim.
"""

import math
import os
import re
from collections import OrderedDict

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

STOP_WORDS = {
    "can", "the", "and", "for", "are", "not", "has", "had", "was",
    "how", "what", "when", "where", "who", "which", "does", "have",
    "from", "this", "that", "with", "its", "you", "all", "any",
    "than", "been", "being", "will", "would", "should", "could",
    "may", "might", "shall", "must", "need", "there", "their",
    "about", "into", "over", "your", "more", "also", "just",
    "get", "do", "am", "if", "my",
}

# Query-word variants that appear in the documents.
SYNONYMS = {
    "approves": ["approval"],
    "approve": ["approval"],
    "slack": ["software"],
    "install": ["installed", "installation"],
    "leave": ["leaves"],
    "airfare": ["air travel"],
    "trips": ["travel", "journeys"],
    "reimbursement": ["reimbursable", "reimburse"],
    "lose": ["lost", "stolen"],
    "contact": ["report", "helpdesk"],
    "email": ["emails"],
    "use": ["used"],
}

# Multi-word concepts: query phrase -> phrases present in the documents.
CONCEPTS = {
    "lwp": {
        "query": ["leave without pay"],
        "doc": ["lwp", "leave without pay"],
    },
    "personal-device": {
        "query": ["personal phone", "personal device", "own phone", "my phone", "phone", "mobile"],
        "doc": ["personal device", "personal devices"],
    },
    "work-from-home": {
        "query": ["work from home", "working from home", "wfh"],
        "doc": ["work-from-home", "work from home", "wfh"],
    },
}

CONCEPT_WEIGHT = 10.0
PHRASE_WEIGHT = 4.0
DOC_COVERAGE_WEIGHT = 1.0
MIN_HITS = 2

# Bigrams containing only function words carry no topical signal.
WEAK_PHRASE_WORDS = {
    "can", "may", "my", "your", "the", "on", "in", "for", "get",
    "also", "do", "and", "i", "to", "of", "with",
}

PERMISSIVE_MARKERS = [
    "may be", "is entitled", "are entitled", "permitted", "reimbursable",
    "entitled to",
]
PROHIBITIVE_MARKERS = [
    "must not", "cannot", "may not", "not be used", "not permitted",
    "prohibited",
]


def retrieve_documents():
    """loads all 3 policy files, indexes by document name and section number

    Each section entry is (heading, text). Missing files are logged and
    excluded rather than hallucinated.
    """
    index = OrderedDict()
    for doc_name, rel_path in DOCUMENTS.items():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.normpath(os.path.join(script_dir, rel_path))
        if not os.path.isfile(full_path):
            print(f"[WARN] File not found: {full_path} — excluded from index.")
            continue
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        index[doc_name] = parse_sections(content)
    return index


def parse_sections(content):
    """Parse a policy document into section_number -> (heading, text)."""
    sections = OrderedDict()
    current_section = None
    current_lines = []
    current_heading = ""
    pending_heading = ""

    for line in content.splitlines():
        if re.match(r"^═+", line):
            continue
        major_header = re.match(r"^(\d+)\.\s+(.+)$", line)
        subsection_match = re.match(r"^(\d+\.\d+)\s", line)

        if major_header and not subsection_match:
            pending_heading = major_header.group(2).strip()
            continue

        if subsection_match:
            sec_num = subsection_match.group(1)
            if current_section is not None and current_lines:
                sections[current_section] = (
                    current_heading,
                    "\n".join(current_lines).strip(),
                )
            current_section = sec_num
            current_heading = pending_heading
            current_lines = [line.strip()]
        elif current_section is not None:
            stripped = line.strip()
            if stripped:
                current_lines.append(stripped)

    if current_section is not None and current_lines:
        sections[current_section] = (
            current_heading,
            "\n".join(current_lines).strip(),
        )

    return sections


def build_keyword_weights(sections_by_doc):
    """Build per-keyword IDF weights: rarer words across sections score higher."""
    doc_count = {}
    total_sections = 0
    for doc_name, sections in sections_by_doc.items():
        for sec_num, (heading, text) in sections.items():
            total_sections += 1
            words = set(re.findall(r"\w{3,}", (heading + " " + text).lower()))
            for w in words:
                doc_count[w] = doc_count.get(w, 0) + 1
    weights = {}
    for w, cnt in doc_count.items():
        weights[w] = math.log((total_sections + 1) / (cnt + 1)) + 1
    return weights


def decompose_question(question):
    """Split a question into concepts, remaining keywords, bigrams, and mode.

    Returns (concepts, keywords, bigrams, is_permission).
    """
    ql = question.lower()
    concepts = []
    blacklist = set()
    for canon, mapping in CONCEPTS.items():
        for qphrase in mapping["query"]:
            if qphrase in ql:
                concepts.append(canon)
                blacklist.update(re.findall(r"\w{3,}", qphrase))
                break

    keywords = set(re.findall(r"\w{3,}", ql)) - STOP_WORDS - blacklist

    # Phrase n-grams (with synonym-expanded variants) for contiguous matches.
    # Bigrams that are mostly function words carry no topical signal.
    words = [w for w in re.findall(r"\w{3,}", ql) if w not in blacklist]
    bigrams = set()
    for i in range(len(words) - 1):
        a, b = words[i], words[i + 1]
        if a in WEAK_PHRASE_WORDS or b in WEAK_PHRASE_WORDS:
            continue
        for x in ([a] if a not in SYNONYMS else [a] + SYNONYMS[a]):
            for y in ([b] if b not in SYNONYMS else [b] + SYNONYMS[b]):
                bigrams.add(x + " " + y)

    is_permission = bool(re.match(r"^(can|may|am i|is it|are we)", ql)) or "allowed" in ql
    return concepts, keywords, bigrams, is_permission


def score_section(doc_name, sec_num, question, weights, index):
    """Score a single section against a decomposed question."""
    heading, text = index[doc_name][sec_num]
    concepts, keywords, bigrams, is_permission = question[0], question[1], question[2], question[3]

    tl = text.lower()
    hl = heading.lower()

    score = 0.0
    hits = set()

    for canon in concepts:
        if any(dp in tl or dp in hl for dp in CONCEPTS[canon]["doc"]):
            score += CONCEPT_WEIGHT
            hits.add(canon)

    for w in keywords:
        if w in tl:
            score += weights.get(w, 1.0)
            hits.add(w)
        elif w in SYNONYMS:
            for s in SYNONYMS[w]:
                if s in tl:
                    score += weights.get(s, 1.0) * 0.9
                    hits.add(w)
                    break
        if w in hl:
            score += weights.get(w, 1.0) * 0.5

    for bigram in bigrams:
        if bigram in tl:
            score += PHRASE_WEIGHT
            hits.add(bigram)

    if is_permission:
        if any(p in tl for p in PERMISSIVE_MARKERS):
            score += 3.0
        if any(p in tl for p in PROHIBITIVE_MARKERS):
            score -= 2.0

    return score, hits


def doc_keyword_coverage(question, sections_by_doc):
    """Count distinct query keywords that literally appear anywhere in each
    document. Documents with more direct topical overlap are favoured on
    near-ties, which stops a weak synonym match in an off-topic document
    from winning (e.g., an LWP clause beating an allowance clause)."""
    concepts, keywords, bigrams, is_permission = question
    coverage = {}
    for doc_name, sections in sections_by_doc.items():
        haystack = " ".join(
            heading + " " + text for heading, text in sections.values()
        ).lower()
        coverage[doc_name] = sum(1 for w in keywords if w in haystack)
    return coverage


def best_section(question, sections_by_doc, weights):
    """Return the single best (doc_name, section_number, score, hits) or None."""
    coverage = doc_keyword_coverage(question, sections_by_doc)
    best = None
    for doc_name, sections in sections_by_doc.items():
        for sec_num in sections:
            score, hits = score_section(doc_name, sec_num, question, weights, sections_by_doc)
            if not hits:
                continue
            effective = score + DOC_COVERAGE_WEIGHT * coverage[doc_name]
            candidate = (doc_name, sec_num, score, len(hits), hits, effective)
            if best is None or candidate[5] > best[5]:
                best = candidate
    return best


def answer_question(question, index, weights=None):
    """searches indexed documents, returns single-source answer + citation OR refusal template"""
    question_q = decompose_question(question)
    weights = weights or build_keyword_weights(index)

    result = best_section(question_q, index, weights)
    if result is None:
        return REFUSAL_TEMPLATE

    doc_name, sec_num, score, hit_count, hits, effective = result
    if hit_count < MIN_HITS:
        return REFUSAL_TEMPLATE

    heading, text = index[doc_name][sec_num]

    return (
        f"{text}\n"
        f"\n"
        f"Source: {doc_name}, section {sec_num}"
    )


def main():
    print("=" * 60)
    print("UC-X Policy QA Agent")
    print("Type your question about company policy, or 'quit' to exit.")
    print("=" * 60)

    index = retrieve_documents()
    weights = build_keyword_weights(index)
    doc_names = list(index.keys())
    total_sections = sum(len(s) for s in index.values())
    print(f"\nIndexed {len(doc_names)} document(s), {total_sections} sections.")
    for doc_name in doc_names:
        print(f"  - {doc_name} ({len(index[doc_name])} sections)")

    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, index, weights)

        if answer == REFUSAL_TEMPLATE:
            print("\n" + answer + "\n")
        else:
            print()
            print(answer)
            print()

        for phrase in HEDGING_PHRASES:
            if phrase in answer.lower():
                print(f"[VIOLATION] Hedging phrase detected: '{phrase}'")
                break


if __name__ == "__main__":
    main()