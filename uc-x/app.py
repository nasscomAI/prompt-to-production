"""
UC-X — Ask My Documents
Interactive CLI policy Q&A agent.
Uses the RICE enforcement rules from agents.md and the two skills from skills.md.

Run:
    python app.py
"""

import math
import os
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLICY_FILES = [
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard practice",
    "employees are generally expected",
]

# Stop words — keep domain-significant words.
STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could must need ought "
    "i me my we our you your he she it its they them their this that "
    "these those what which who whom how where when why "
    "and or but not nor so yet for if then else than too also "
    "very much more most some any all each every both few many "
    "of in on at by to from with into through during before after "
    "above below between under over about around "
    "up down out off away back again still already just even "
    "here there now then always never sometimes often "
    "get got make made take taken give given went come came "
    "say said tell told know knew think thought see saw "
    "want let find found keep kept put set run try "
    "call help show move live play turn start seem look feel become "
    "same different new old good great big small long short high low "
    "first last next other another right well really only "
    "company view culture flexible general opinion".split()
)

# Synonym map: query word -> additional terms to search.
SYNONYMS: dict[str, list[str]] = {
    "phone": ["device", "devices", "mobile"],
    "mobile": ["phone", "device", "devices"],
    "laptop": ["device", "devices", "computer", "laptops"],
    "laptops": ["device", "devices", "computer", "laptop"],
    "computer": ["device", "devices", "laptop", "desktop"],
    "install": ["software", "installation"],
    "installation": ["install", "software"],
    "software": ["install", "installation"],
    "approve": ["approval", "approves", "approved", "pre-approved"],
    "approves": ["approval", "approve", "approved", "pre-approved"],
    "approval": ["approve", "approves", "approved", "pre-approved"],
    "approved": ["approval", "approve", "approves"],
    "home": ["wfh"],
    "files": ["data", "access", "store"],
    "carry": ["forward"],
    "forward": ["carry"],
    "claim": ["claimed", "claims"],
    "claims": ["claim", "claimed"],
    "claimed": ["claim", "claims"],
    "receipts": ["receipt"],
    "use": ["access", "using", "used"],
    "used": ["use", "access", "using"],
    "personal": ["byod"],
    "pay": ["paid", "lwp", "lop"],
    "lwp": ["pay", "leave"],
    "without": ["lwp"],
}


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    """Lowercase alpha tokens, removing stop words and very short tokens.
    Hyphenated words are split into components alongside the original."""
    raw_words = re.findall(r"[a-z][a-z-]*[a-z]|[a-z]+", text.lower())
    result: list[str] = []
    for w in raw_words:
        if len(w) <= 2 or w in STOP_WORDS:
            continue
        result.append(w)
        # Split hyphenated words into components
        if "-" in w:
            for part in w.split("-"):
                if len(part) > 2 and part not in STOP_WORDS and part not in result:
                    result.append(part)
    return result


def tokenize_for_search(text: str) -> list[str]:
    """Like tokenize but adds synonyms for broader matching."""
    raw = tokenize(text)
    expanded: list[str] = []
    seen: set[str] = set()
    for w in raw:
        if w not in seen:
            expanded.append(w)
            seen.add(w)
        for syn in SYNONYMS.get(w, []):
            if syn not in seen:
                expanded.append(syn)
                seen.add(syn)
    return expanded


# ---------------------------------------------------------------------------
# Skill 1 — retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(
    filepaths: list[str],
) -> dict[str, dict[str, str]]:
    """
    Loads policy files and indexes content by document name and section number.

    Returns:
        {
            "policy_hr_leave.txt": {
                "1.1": "section text ...",
                "2.6": "section text ...",
            },
            ...
        }

    Raises:
        FileNotFoundError  – if a file path does not exist or is unreadable.
        ValueError          – if no section headers can be parsed from a file.
    """
    index: dict[str, dict[str, str]] = {}

    for filepath in filepaths:
        abs_path = os.path.abspath(filepath)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"Policy file not found: {abs_path}")

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as exc:
            raise FileNotFoundError(f"Cannot read policy file: {abs_path}") from exc

        doc_name = os.path.basename(abs_path)

        # Find sub-section starts (e.g. "2.6 ...")
        sub_pattern = re.compile(r"^(\d+\.\d+)\s", re.MULTILINE)
        sub_matches = list(sub_pattern.finditer(content))

        # Boundaries: major headings and separator lines
        major_pattern = re.compile(r"^(\d+)\.\s+[A-Z]", re.MULTILINE)
        sep_pattern = re.compile(r"^[═]{3,}", re.MULTILINE)
        major_starts = {m.start() for m in major_pattern.finditer(content)}
        sep_starts = {m.start() for m in sep_pattern.finditer(content)}
        boundaries = sorted(major_starts | sep_starts)

        if not sub_matches:
            raise ValueError(
                f"No section headers (e.g. '2.6 ...') found in {doc_name}."
            )

        sections: dict[str, str] = {}
        for i, match in enumerate(sub_matches):
            section_num = match.group(1)
            start = match.start()
            next_sub = (
                sub_matches[i + 1].start()
                if i + 1 < len(sub_matches)
                else len(content)
            )

            end = next_sub
            for b in boundaries:
                if start < b < next_sub:
                    end = b
                    break

            section_text = content[start:end].strip()
            section_text = re.sub(r"[═]+", "", section_text).strip()
            sections[section_num] = section_text

        index[doc_name] = sections

    return index


# ---------------------------------------------------------------------------
# TF-IDF search engine (stdlib only)
# ---------------------------------------------------------------------------

class SectionSearcher:
    """TF-IDF based searcher over indexed policy sections."""

    def __init__(self, index: dict[str, dict[str, str]]):
        self.index = index
        self.corpus: list[tuple[str, str, list[str]]] = []
        self.doc_freq: Counter[str] = Counter()

        all_token_sets: list[set[str]] = []
        for doc_name, sections in index.items():
            for sec_num, sec_text in sections.items():
                tokens = tokenize_for_search(sec_text)
                self.corpus.append((doc_name, sec_num, tokens))
                all_token_sets.append(set(tokens))

        for token_set in all_token_sets:
            for token in token_set:
                self.doc_freq[token] += 1

        self.n_docs = len(self.corpus)

    def search(
        self, question: str, top_k: int = 15
    ) -> list[tuple[float, str, str, str]]:
        """
        Returns list of (score, doc_name, section_num, section_text)
        sorted by TF-IDF relevance, descending.
        """
        q_tokens = tokenize_for_search(question)
        if not q_tokens:
            return []

        original_words = set(tokenize(question))
        q_tf = Counter(q_tokens)

        results: list[tuple[float, str, str, str]] = []
        for doc_name, sec_num, sec_tokens in self.corpus:
            if not sec_tokens:
                continue
            sec_tf = Counter(sec_tokens)
            score = 0.0
            matched_original = 0
            for term, q_count in q_tf.items():
                if term not in sec_tf:
                    continue
                if term in original_words:
                    matched_original += 1
                df = self.doc_freq.get(term, 1)
                idf = math.log(1 + self.n_docs / df)
                tf_sec = sec_tf[term] / len(sec_tokens)
                tf_q = q_count / len(q_tokens)
                score += tf_sec * tf_q * (idf ** 2)

            if matched_original > 1:
                score *= 1 + 0.5 * matched_original

            if score > 0:
                sec_text = self.index[doc_name][sec_num]
                results.append((score, doc_name, sec_num, sec_text))

        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]


# ---------------------------------------------------------------------------
# Skill 2 — answer_question
# ---------------------------------------------------------------------------

# Generic words too common across all policy docs to be meaningful alone
_GENERIC_WORDS = frozenset({
    "work", "working", "employee", "employees", "day", "days",
    "department", "cmc", "policy",
})


def _is_relevant(
    top_score: float,
    question: str,
    top_text: str,
) -> bool:
    """
    Determine if the top result is genuinely relevant to the question.
    """
    if top_score < 0.01:
        return False

    q_expanded = set(tokenize_for_search(question))
    sec_expanded = set(tokenize_for_search(top_text))
    overlap = q_expanded & sec_expanded
    meaningful = overlap - _GENERIC_WORDS
    return len(meaningful) >= 1


def _get_chapter(sec_num: str) -> str:
    """Extract chapter number from section number (e.g. '5.2' -> '5')."""
    return sec_num.split(".")[0]


def answer_question(
    question: str,
    index: dict[str, dict[str, str]],
    searcher: SectionSearcher,
) -> str:
    """
    Searches indexed policy documents and returns a single-source answer
    with citation, or the verbatim refusal template.

    Enforcement rules applied:
        1. Never combine claims from two different documents.
        2. Never use hedging phrases.
        3. If not in documents — exact refusal template, no variations.
        4. Cite source document name + section number for every claim.
        5. Single-source answer or clean refusal on ambiguity.
        6. Never drop conditions from policy statements.
    """
    results = searcher.search(question, top_k=15)

    if not results:
        return REFUSAL_TEMPLATE

    # ----- Enforcement: Single-source rule (Rule 1 & 5) -----
    doc_scores: dict[str, float] = {}
    doc_sections: dict[str, list[tuple[float, str, str]]] = {}
    for score, doc_name, sec_num, sec_text in results:
        doc_scores[doc_name] = doc_scores.get(doc_name, 0.0) + score
        doc_sections.setdefault(doc_name, []).append((score, sec_num, sec_text))

    best_doc = max(doc_scores, key=lambda d: doc_scores[d])
    best_sections = doc_sections[best_doc]
    top_score = best_sections[0][0]
    top_text = best_sections[0][2]

    if not _is_relevant(top_score, question, top_text):
        return REFUSAL_TEMPLATE

    # Identify the primary chapter from the top-scoring section
    primary_chapter = _get_chapter(best_sections[0][1])

    # Collect all sections from the best document that scored above threshold
    threshold = top_score * 0.15
    all_matching = [
        (s, sn, st) for s, sn, st in best_sections if s >= threshold
    ]

    # Prioritize sections from the primary chapter, then include others
    primary = [(s, sn, st) for s, sn, st in all_matching if _get_chapter(sn) == primary_chapter]
    other = [(s, sn, st) for s, sn, st in all_matching if _get_chapter(sn) != primary_chapter]

    # Take up to 3 primary chapter sections, then fill with others up to 3 total
    selected = primary[:3]
    remaining_slots = 3 - len(selected)
    if remaining_slots > 0:
        selected.extend(other[:remaining_slots])

    # Sort by section number for readability
    selected.sort(key=lambda x: list(map(int, x[1].split("."))))

    # Build answer with mandatory citations (Rule 4)
    # Preserve full policy text — never drop conditions (Rule 6)
    answer_parts: list[str] = []
    for _score, sec_num, sec_text in selected:
        answer_parts.append(f"[{best_doc}, Section {sec_num}]\n{sec_text}")

    answer = "\n\n".join(answer_parts)

    # ----- Enforcement: No hedging phrases (Rule 2) -----
    answer_lower = answer.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in answer_lower:
            return REFUSAL_TEMPLATE

    return answer


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A Agent (HR Leave · IT Acceptable Use · Finance)")
    print("=" * 60)
    print()

    # Skill 1: retrieve_documents
    try:
        index = retrieve_documents(POLICY_FILES)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    searcher = SectionSearcher(index)

    doc_names = ", ".join(index.keys())
    total_sections = sum(len(secs) for secs in index.values())
    print(f"Loaded {len(index)} documents ({total_sections} sections): {doc_names}")
    print()
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.")
    print("-" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # Skill 2: answer_question
        answer = answer_question(question, index, searcher)
        print(f"\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
