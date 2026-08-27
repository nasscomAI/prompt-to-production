"""
UC-X — Ask My Documents
Interactive CLI for policy document Q&A with keyword-based retrieval.
Single-source attribution enforced. No hedging. Mandatory citations.
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLICY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

STOP_WORDS = {
    "is", "the", "a", "an", "can", "i", "my", "what", "who", "how",
    "do", "does", "on", "in", "of", "to", "for", "from", "and", "or",
    "with", "it", "be", "that", "this", "at", "by", "are", "was",
    "were", "have", "has", "had", "will", "would", "should", "could",
    "may", "not", "no", "all", "if", "their", "there", "they", "them",
    "then", "than", "its", "any", "each", "both", "same", "use",
    "work", "working",
}

# Minimum number of distinct keywords that must match for a section to be relevant
MIN_KEYWORD_MATCH = 2

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Synonym expansions: keyword -> list of alternative forms to search for.
# Only include direct semantic equivalents, not loosely related terms.
SYNONYMS = {
    "install": ["installation", "installed", "installing", "software"],
    "software": ["install", "installed", "installation"],
    "approve": ["approval", "approved", "approves"],
    "approves": ["approval", "approved", "approve"],
    "approval": ["approve", "approved", "approves"],
    "approved": ["approval", "approve", "approves"],
    "carry": ["carry-forward", "carried"],
    "forward": ["carry-forward"],
    "claim": ["claims", "claimed", "claiming"],
    "claims": ["claim", "claimed"],
    "receipt": ["receipts"],
    "receipts": ["receipt"],
    "meal": ["meals"],
    "meals": ["meal"],
    "leave": ["lwp", "leave"],
    "pay": ["lwp", "paid", "loss of pay"],
    "without": ["lwp"],
    "lwp": ["leave without pay"],
    "da": ["daily allowance"],
    "phone": ["phones", "mobile", "device", "devices"],
    "personal": ["byod", "personal device", "personal devices"],
    "home": ["work-from-home", "wfh", "home office"],
    "equipment": ["allowance"],
    "allowance": ["equipment", "entitlement", "entitled"],
    "office": ["home office"],
    "laptop": ["laptops", "corporate device", "corporate devices"],
    "laptops": ["laptop", "corporate device", "corporate devices"],
    "unused": ["carry forward", "carry-forward"],
    "annual": ["year", "yearly"],
    "slack": ["software"],
    "files": ["data", "access", "store"],
}

# ---------------------------------------------------------------------------
# Document Loading and Parsing
# ---------------------------------------------------------------------------


def load_document(filepath):
    """Load a document file and return its text content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_sections(text, document_name):
    """
    Parse a policy document into sections.
    Each section starts with a numbered line like '1.1 ...', '2.3 ...'.
    Returns a list of dicts: {document_name, section_number, section_text}
    """
    sections = []
    lines = text.split("\n")
    current_section = None
    current_text_lines = []

    section_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    separator_pattern = re.compile(r"^[═─━]{3,}$")
    group_header_pattern = re.compile(r"^\d+\.\s+[A-Z]")

    for line in lines:
        stripped = line.strip()
        if separator_pattern.match(stripped) or group_header_pattern.match(stripped):
            if current_section is not None:
                sections.append({
                    "document_name": document_name,
                    "section_number": current_section,
                    "section_text": "\n".join(current_text_lines).strip(),
                })
                current_section = None
                current_text_lines = []
            continue

        match = section_pattern.match(line)
        if match:
            if current_section is not None:
                sections.append({
                    "document_name": document_name,
                    "section_number": current_section,
                    "section_text": "\n".join(current_text_lines).strip(),
                })
            current_section = match.group(1)
            current_text_lines = [line]
        else:
            if current_section is not None:
                current_text_lines.append(line)

    if current_section is not None:
        sections.append({
            "document_name": document_name,
            "section_number": current_section,
            "section_text": "\n".join(current_text_lines).strip(),
        })

    return sections


def load_all_documents():
    """Load and parse all policy documents into sections."""
    all_sections = []
    for filename in POLICY_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found. Skipping.")
            continue
        text = load_document(filepath)
        sections = parse_sections(text, filename)
        all_sections.extend(sections)
    return all_sections


# ---------------------------------------------------------------------------
# Keyword Search and Retrieval
# ---------------------------------------------------------------------------


def extract_keywords(question):
    """Extract significant keywords from the question, removing stop words."""
    words = re.findall(r"[a-z]+", question.lower())
    keywords = [w for w in words if w not in STOP_WORDS]
    return keywords


def keyword_in_text(keyword, text_lower):
    """
    Check if a keyword or its synonyms appear in the text.
    For short keywords (<=3 chars), use word-boundary matching to avoid false positives.
    """
    # Direct match
    if len(keyword) <= 3:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            return True
    else:
        if keyword in text_lower:
            return True

    # Check synonyms
    if keyword in SYNONYMS:
        for syn in SYNONYMS[keyword]:
            if len(syn) <= 3:
                if re.search(r'\b' + re.escape(syn) + r'\b', text_lower):
                    return True
            else:
                if syn in text_lower:
                    return True

    return False


def score_section(section, keywords):
    """Score a section by counting how many distinct keywords match in its text."""
    text_lower = section["section_text"].lower()
    score = 0
    for keyword in keywords:
        if keyword_in_text(keyword, text_lower):
            score += 1
    return score


def retrieve_documents(question, all_sections):
    """
    Search all sections for relevance to the question.
    Returns top-scoring sections from a SINGLE document only.

    Document selection uses the highest single-section score (best match).
    """
    keywords = extract_keywords(question)
    if not keywords:
        return []

    # Score all sections
    scored_sections = []
    for section in all_sections:
        score = score_section(section, keywords)
        if score >= MIN_KEYWORD_MATCH:
            scored_sections.append({**section, "score": score})

    if not scored_sections:
        return []

    # Group by document — use MAX section score to pick best document
    doc_max_score = {}
    doc_sections = {}
    for s in scored_sections:
        doc = s["document_name"]
        if doc not in doc_max_score:
            doc_max_score[doc] = 0
            doc_sections[doc] = []
        if s["score"] > doc_max_score[doc]:
            doc_max_score[doc] = s["score"]
        doc_sections[doc].append(s)

    # Select the document with highest max section score
    best_doc = max(doc_max_score, key=doc_max_score.get)

    # Return sections from best document, sorted by score descending
    results = sorted(doc_sections[best_doc], key=lambda x: x["score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Answer Formulation
# ---------------------------------------------------------------------------


def answer_question(question, retrieved_sections):
    """
    Formulate an answer from retrieved sections.
    If no sections found, return the refusal template.
    """
    if not retrieved_sections:
        return REFUSAL_TEMPLATE

    top_score = retrieved_sections[0]["score"]

    # Only include sections with score at least 70% of top score
    relevant = [s for s in retrieved_sections if s["score"] >= top_score * 0.7]

    # Limit to top 3 most relevant sections
    relevant = relevant[:3]

    # Build answer
    doc_name = relevant[0]["document_name"]
    answer_parts = []
    answer_parts.append(f"Source: {doc_name}\n")

    for section in relevant:
        section_text = section["section_text"].strip()
        cleaned_lines = []
        for line in section_text.split("\n"):
            cleaned_lines.append(line.strip())
        cleaned_text = " ".join(cleaned_lines)

        answer_parts.append(
            f"[{doc_name}, Section {section['section_number']}]: {cleaned_text}"
        )

    return "\n".join(answer_parts)


# ---------------------------------------------------------------------------
# Main Interactive Loop
# ---------------------------------------------------------------------------


def main():
    """Run the interactive Q&A loop."""
    print("=" * 60)
    print("UC-X — Ask My Documents (Policy Q&A)")
    print("=" * 60)
    print("Loaded policy documents:")
    for f in POLICY_FILES:
        print(f"  - {f}")
    print()
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    # Load all documents
    all_sections = load_all_documents()
    if not all_sections:
        print("ERROR: No policy documents could be loaded. Exiting.")
        sys.exit(1)

    print(f"Loaded {len(all_sections)} sections from {len(POLICY_FILES)} documents.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit"):
            print("Exiting.")
            break

        # Retrieve relevant sections
        results = retrieve_documents(question, all_sections)

        # Formulate and print answer
        answer = answer_question(question, results)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
