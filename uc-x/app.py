"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question per agents.md and skills.md.

Enforcement (from agents.md):
  - Never combine claims from two different documents into a single answer
  - Never use hedging phrases
  - If question is not in the documents, use the refusal template exactly
  - Cite source document name and section number for every factual claim
"""
import os
import re
import sys


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
    "generally",
    "usually",
    "in most cases",
    "it is worth noting",
]

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = {
    "policy_hr_leave.txt": os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
}

# Category-to-document mapping for disambiguation
CATEGORY_DOCUMENTS = {
    "leave": "policy_hr_leave.txt",
    "sick": "policy_hr_leave.txt",
    "maternity": "policy_hr_leave.txt",
    "paternity": "policy_hr_leave.txt",
    "lwp": "policy_hr_leave.txt",
    "encashment": "policy_hr_leave.txt",
    "holiday": "policy_hr_leave.txt",
    "grievance": "policy_hr_leave.txt",
    "password": "policy_it_acceptable_use.txt",
    "software": "policy_it_acceptable_use.txt",
    "install": "policy_it_acceptable_use.txt",
    "personal device": "policy_it_acceptable_use.txt",
    "byod": "policy_it_acceptable_use.txt",
    "email": "policy_it_acceptable_use.txt",
    "internet": "policy_finance_reimbursement.txt",
    "reimbursement": "policy_finance_reimbursement.txt",
    "travel": "policy_finance_reimbursement.txt",
    "hotel": "policy_finance_reimbursement.txt",
    "da": "policy_finance_reimbursement.txt",
    "meal": "policy_finance_reimbursement.txt",
    "home office": "policy_finance_reimbursement.txt",
    "work from home": "policy_finance_reimbursement.txt",
    "equipment": "policy_finance_reimbursement.txt",
    "training": "policy_finance_reimbursement.txt",
    "mobile phone": "policy_finance_reimbursement.txt",
    "claim": "policy_finance_reimbursement.txt",
}


def retrieve_documents(policy_files: dict | None = None) -> dict:
    """
    Loads all three policy .txt files and indexes them by document name
    and section number.

    Returns:
        {
            "documents": {
                "policy_hr_leave.txt": {
                    "sections": {"1.1": "text", "1.2": "text", "2.3": "text", ...},
                    "section_headers": {"1": "PURPOSE AND SCOPE", "2": "ANNUAL LEAVE", ...},
                },
                ...
            },
            "all_entries": [
                {"doc": str, "section": str, "section_title": str, "text": str, "keywords": set},
                ...
            ]
        }

    Enforcement (from skills.md):
      - If any file cannot be read or is missing section numbering, halt and report
    """
    if policy_files is None:
        policy_files = POLICY_FILES

    documents = {}
    all_entries = []

    for doc_name, file_path in policy_files.items():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"ERROR: Could not find {file_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not read {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

        if not lines:
            print(f"ERROR: {file_path} is empty.", file=sys.stderr)
            sys.exit(1)

        sections = {}
        section_headers = {}
        current_section_num = None
        current_section_title = ""

        section_header_re = re.compile(r"^(\d+)\.\s+(.+)$")
        clause_re = re.compile(r"^(\d+\.\d+)\s+(.+)$")

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("═") or stripped.startswith("---"):
                continue

            sec_match = section_header_re.match(stripped)
            if sec_match:
                current_section_num = sec_match.group(1)
                current_section_title = sec_match.group(2).strip()
                section_headers[current_section_num] = current_section_title
                continue

            clause_match = clause_re.match(stripped)
            if clause_match:
                clause_id = clause_match.group(1)
                clause_text = clause_match.group(2).strip()
                sections[clause_id] = clause_text
                continue

            # Continuation line
            if current_section_num and sections:
                last_id = list(sections.keys())[-1]
                sections[last_id] += " " + stripped

        if not sections:
            print(
                f"ERROR: No numbered sections found in {doc_name} ({file_path}).",
                file=sys.stderr,
            )
            sys.exit(1)

        documents[doc_name] = {
            "sections": sections,
            "section_headers": section_headers,
        }

        # Build indexed entries with keywords
        for sec_id, sec_text in sections.items():
            sec_num = sec_id.split(".")[0]
            title = section_headers.get(sec_num, "")
            combined = f"{title} {sec_text}".lower()
            keywords = set(re.findall(r"\b\w{3,}\b", combined))
            # Add normalized forms for better matching
            normalized = {_normalize_word(w) for w in keywords}
            all_entries.append({
                "doc": doc_name,
                "section": sec_id,
                "section_title": title,
                "text": sec_text,
                "keywords": keywords | normalized,
            })

    return {"documents": documents, "all_entries": all_entries}


def _expand_abbreviations(text: str) -> str:
    """Expand known policy abbreviations for better matching (word-boundary only)."""
    abbreviations = {
        "lwp": "leave without pay",
        "lop": "loss of pay",
        "da": "daily allowance",
        "cmc": "city municipal corporation",
        "mfa": "multi factor authentication",
        "byod": "bring your own device personal device",
    }
    expanded = text.lower()
    for abbr, full in abbreviations.items():
        expanded = re.sub(r"\b" + re.escape(abbr) + r"\b", full, expanded)
    return expanded


def _normalize_word(word: str) -> str:
    """
    Simple normalization: strip common suffixes for matching plurals,
    verb tenses, and other variants.
    """
    w = word.lower()
    # Irregular forms
    irregulars = {
        "lost": "lose", "left": "leave", "changed": "change",
        "required": "require", "approved": "approve",
        "submitted": "submit", "permitted": "permit",
        "entitled": "entitle", "claimed": "claim",
        "exceeding": "exceed", "taken": "take",
        "connected": "connect", "stored": "store",
        "installed": "install", "disabled": "disable",
        "circumvented": "circumvent", "classified": "classify",
        "demonstrated": "demonstrate", "declared": "declare",
        "governed": "govern", "managed": "manage",
        "forfeited": "forfeit", "encashed": "encash",
        "reported": "report", "used": "use",
    }
    if w in irregulars:
        return irregulars[w]
    # Strip common suffixes
    for suffix in ("ing", "tion", "ment", "ness", "able", "ible", "ally"):
        if w.endswith(suffix) and len(w) > len(suffix) + 3:
            return w[:-len(suffix)]
    for suffix in ("ed", "es", "er", "ly", "al"):
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            return w[:-len(suffix)]
    if w.endswith("s") and len(w) > 3:
        return w[:-1]
    return w


def _extract_question_keywords(question: str) -> set:
    """Extract meaningful keywords from the question."""
    stop_words = {
        "can", "what", "the", "for", "and", "are", "does", "how", "who",
        "is", "my", "me", "i", "a", "an", "to", "in", "on", "of", "from",
        "it", "that", "this", "be", "with", "if", "or", "not", "do", "at",
        "by", "am", "was", "were", "been", "have", "has", "had", "will",
        "would", "could", "should", "may", "might",
    }
    words = re.findall(r"\b\w{2,}\b", question.lower())
    keywords = {w for w in words if w not in stop_words}
    # Also add normalized forms for better matching
    normalized = {_normalize_word(w) for w in keywords}
    return keywords | normalized


def _detect_target_document(question: str) -> str | None:
    """
    Detect which document the question is most likely about based on
    category keywords. Returns None if ambiguous.
    """
    q_lower = question.lower()
    matches = {}
    for cat, doc in CATEGORY_DOCUMENTS.items():
        if cat in q_lower:
            matches[doc] = matches.get(doc, 0) + 1

    if len(matches) == 1:
        return list(matches.keys())[0]
    return None


def _score_entry(question_keywords: set, entry: dict, question: str = "") -> int:
    """
    Score an entry's relevance to the question.
    Combines keyword overlap with phrase-level matching for precision.
    """
    # Base score: keyword overlap (already includes normalized forms from indexing)
    score = len(question_keywords & entry["keywords"])

    # Expand abbreviations in text for phrase/action matching
    text_lower = _expand_abbreviations(entry["text"])

    # Bonus: exact word-boundary phrase matching (2+ word phrases from question)
    words = re.findall(r"\b\w+\b", question.lower())
    # Filter out very common short words for phrase matching
    phrase_stop = {"can", "the", "for", "and", "are", "does", "what", "who",
                   "is", "my", "a", "an", "to", "in", "on", "of", "from",
                   "it", "that", "be", "with", "if", "or", "not", "do", "at"}
    phrase_words = [w for w in words if w not in phrase_stop and len(w) >= 3]

    for i in range(len(phrase_words) - 1):
        bigram = f"{phrase_words[i]} {phrase_words[i+1]}"
        if re.search(r"\b" + re.escape(bigram) + r"\b", text_lower):
            score += 3
        if i < len(phrase_words) - 2:
            trigram = f"{phrase_words[i]} {phrase_words[i+1]} {phrase_words[i+2]}"
            if re.search(r"\b" + re.escape(trigram) + r"\b", text_lower):
                score += 5

    # Bonus: if question asks "who" or about "approval" and entry contains approval words
    q_lower = question.lower()
    if "who" in q_lower or "approv" in q_lower:
        if "requires" in text_lower or "approval" in text_lower:
            score += 2

    # Bonus: specific product/tool names from the question appearing in text
    # Exclude common English words that happen to be capitalized
    common_caps = {"Can", "What", "Who", "How", "Is", "Are", "Do", "Does",
                   "Will", "Would", "Could", "Should", "May", "Might", "The",
                   "This", "That", "My", "If", "When", "Where", "Why"}
    specific_terms = re.findall(r"\b[A-Z][a-z]+\b", question)
    for term in specific_terms:
        if term not in common_caps and re.search(r"\b" + term.lower() + r"\b", text_lower):
            score += 4

    # Bonus: action verbs from question matching text (using normalization)
    action_verbs = {"install", "claim", "carry", "approve", "access", "use",
                    "submit", "report", "change", "request", "lose", "connect"}
    text_words = set(re.findall(r"\b\w{3,}\b", text_lower))
    text_normalized = {_normalize_word(w) for w in text_words}
    for verb in action_verbs:
        if verb in question.lower() and (verb in text_words or _normalize_word(verb) in text_normalized):
            score += 2

    return score


def _contains_hedging(text: str) -> bool:
    """Check if text contains any hedging phrases."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in HEDGING_PHRASES)


def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents for relevant content to a user question.
    Returns a single-source answer with citation, or the refusal template.

    Enforcement (from agents.md):
      - Never combine claims from two different documents
      - Never use hedging phrases
      - If not in documents, use refusal template exactly
      - Cite source document name and section number

    Enforcement (from skills.md):
      - If multiple documents could answer, select single most relevant
      - Never blend. If no relevant content, output refusal template.
    """
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    q_keywords = _extract_question_keywords(question)
    if not q_keywords:
        return REFUSAL_TEMPLATE

    # Score all entries

    scored = []
    for entry in index["all_entries"]:
        score = _score_entry(q_keywords, entry, question)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return REFUSAL_TEMPLATE

    # Minimum relevance threshold — if top score is too low, refuse
    # This prevents matching on incidental common words like "working"
    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    if top_score < 3:
        return REFUSAL_TEMPLATE

    # Get all entries with top score
    top_entries = [e for s, e in scored if s == top_score]

    # Check if top entries span multiple documents
    top_docs = {e["doc"] for e in top_entries}

    if len(top_docs) > 1:
        # Cross-document conflict — enforce single-source rule
        # Try to detect which document the question targets
        target_doc = _detect_target_document(question)
        if target_doc and target_doc in top_docs:
            # Filter to target document
            top_entries = [e for e in top_entries if e["doc"] == target_doc]
        else:
            # Ambiguous — pick the entry with highest score from single doc
            # Group by doc, pick doc with most matching entries
            doc_scores = {}
            for s, e in scored:
                doc_scores[e["doc"]] = doc_scores.get(e["doc"], 0) + s
            best_doc = max(doc_scores, key=lambda d: doc_scores[d])
            top_entries = [e for e in top_entries if e["doc"] == best_doc]

    # Take the best single entry
    best = top_entries[0]

    # Format answer with citation
    doc_name = best["doc"]
    section = best["section"]
    text = best["text"]
    section_title = best.get("section_title", "")

    answer = f"According to {doc_name}, section {section}"
    if section_title:
        answer += f" ({section_title})"
    answer += f": {text}"

    # Safety check — no hedging
    if _contains_hedging(answer):
        return REFUSAL_TEMPLATE

    return answer


def main():
    # Load and index all policy documents
    print("Loading policy documents...")
    index = retrieve_documents()

    doc_count = len(index["documents"])
    entry_count = len(index["all_entries"])
    print(f"Indexed {doc_count} documents with {entry_count} sections total.")
    print("Type a question about company policy. Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, index)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
