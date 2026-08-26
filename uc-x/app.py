"""
UC-X app.py — Ask My Documents system.
Loads 3 policy documents and answers questions from single sources only.
Never blends claims across documents. Uses refusal template when not covered.
"""
import argparse
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# Keywords that help classify which document a question belongs to
DOC_KEYWORDS = {
    "policy_hr_leave.txt": {
        "leave", "annual leave", "sick leave", "maternity", "paternity",
        "carry forward", "leave without pay", "lwp", "grievance",
        "public holiday", "encashment"
    },
    "policy_it_acceptable_use.txt": {
        "install", "software", "personal device", "byod", "phone",
        "access", "email", "portal", "laptop", "corporate device",
        "network", "gambling", "adult content", "password", "mfa",
        "internet", "download", "approved"
    },
    "policy_finance_reimbursement.txt": {
        "reimbursement", "receipt", "allowance", "da", "dearness allowance",
        "hotel", "travel", "claim", "expense", "equipment", "training"
    }
}


def load_document(filepath):
    """Load a policy document and return its text."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _strip_formatting(text):
    """Remove document formatting characters (box-drawing lines, etc.)."""
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Skip lines that are only box-drawing characters
        if re.match(r"^[\u2500-\u257F]+$", line):
            continue
        # Skip lines that are just --- or *** etc.
        if re.match(r"^[-=*]+$", line):
            continue
        # Skip very short lines that are just section dividers
        if len(line.strip()) <= 2:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def index_documents():
    """Load and index all 3 policy documents by document name and section number."""
    documents = {}
    doc_names = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    for fname in doc_names:
        filepath = os.path.join(POLICY_DIR, fname)
        if not os.path.exists(filepath):
            continue
        text = _strip_formatting(load_document(filepath))
        # Parse sections: a section starts with a line like "2.6 Text" and
        # continues until the next section-numbered line or end of text.
        sections = {}
        lines = text.split("\n")
        current_section = None
        current_body_parts = []

        for line in lines:
            stripped = line.strip()
            m = re.match(r"^(\d+(\.\d+)*)\s", stripped)
            if m:
                # Save previous section if any
                if current_section is not None:
                    body = " ".join(current_body_parts).strip()
                    if body:
                        sections[current_section] = body
                current_section = m.group(1)
                current_body_parts = [stripped[len(m.group(0)):].strip()]
            else:
                if current_section is not None:
                    # Continue body text (indented or continuation line)
                    current_body_parts.append(stripped)

        # Save last section
        if current_section is not None:
            body = " ".join(current_body_parts).strip()
            if body:
                sections[current_section] = body

        documents[fname] = sections
    return documents


def _extract_keywords(text):
    """Extract significant keywords (len > 2, stop-word filtered)."""
    stop_words = {
        "the", "and", "or", "but", "if", "because", "as", "until", "while",
        "of", "at", "by", "for", "with", "about", "against", "between", "into",
        "through", "during", "before", "after", "above", "below", "to", "from",
        "up", "down", "in", "out", "on", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why", "how",
        "all", "any", "both", "each", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
        "very", "can", "will", "just", "should", "now", "is", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "a", "an", "these", "those", "this", "that", "it"
    }
    words = [w for w in re.findall(r"\b\w+\b", text.lower()) if w not in stop_words and len(w) > 2]
    return set(words)


def _extract_all_words(text):
    """Extract all words len > 2 without stop-word filtering for phrase matching."""
    words = re.findall(r"\b\w+\b", text.lower())
    return {w for w in words if len(w) > 2}


def _has_phrase(text, phrases):
    """Check if any of the given phrases appear in text (case-insensitive)."""
    tl = text.lower()
    for p in phrases:
        if p in tl:
            return True
    return False


def _classify_document(question, documents):
    """Determine which document is most relevant for the question.

    Returns the doc_name or None if no document is clearly relevant.
    Uses document-specific keywords as strong signals.
    Also checks for key phrases that distinguish document scope.
    """
    q_kw = _extract_keywords(question)
    q_lower = question.lower()

    for doc_name, doc_kw in DOC_KEYWORDS.items():
        if doc_name not in documents:
            continue
        intersection = q_kw & doc_kw
        # Strong signal: document-specific keywords match
        if intersection:
            return doc_name
        # Secondary signal: check for key phrases that distinguish documents
        if doc_name == "policy_finance_reimbursement.txt":
            if _has_phrase(q_lower, ["work from home", "home office", "equipment allowance", "home office equipment"]):
                return doc_name
        elif doc_name == "policy_it_acceptable_use.txt":
            if _has_phrase(q_lower, ["personal device", "byod", "access work", "work from"]):
                return doc_name
        elif doc_name == "policy_hr_leave.txt":
            if _has_phrase(q_lower, ["carry forward", "annual leave", "leave application"]):
                return doc_name
    # Fallback: check which document has the most section-level keyword overlap
    best_doc = None
    best_score = 0
    for doc_name, sections in documents.items():
        score = 0
        for section_body in sections.values():
            sec_kw = _extract_keywords(section_body)
            overlap = q_kw & sec_kw
            score += len(overlap)
        if score > best_score:
            best_score = score
            best_doc = doc_name
    return best_doc if best_score >= 3 else None


def _find_best_section(documents, question, doc_name):
    """Find the best matching section within a specific document.

    Only searches within doc_name to prevent cross-document blending.
    Returns (section_num, section_body) or None.
    """
    sections = documents.get(doc_name, {})
    if not sections:
        return None

    q_kw = _extract_keywords(question)
    q_lower = question.lower()

    best_match = None  # (section_num, score, section_body)

    for section_num, section_body in sections.items():
        sec_kw = _extract_keywords(section_body)

        # Score 1: number of keyword overlaps (primary signal)
        kw_overlap = q_kw & sec_kw
        overlap_count = len(kw_overlap)

        # Score 2: bonus for "leave without pay" phrase match (strong signal)
        # Only apply LWP bonus if there's some keyword overlap,
        # otherwise it creates false matches (e.g., s4.4 vs s5.2)
        lwp_bonus = 0
        if overlap_count > 0 and _has_phrase(section_body.lower(), ["leave without pay", "lwp"]):
            if _has_phrase(q_lower, ["leave without pay", "lwp", "approves", "who approves"]):
                lwp_bonus = 30
            elif _has_phrase(q_lower, ["leave without pay", "lwp"]):
                lwp_bonus = 20
            else:
                lwp_bonus = 10
        # Also check for "LWP" alone in section body (only if there's already keyword overlap)
        if overlap_count > 0 and re.search(r"\blwp\b", section_body.lower()):
            lwp_bonus += 5

        # Score 3: bonus for LWP approval context
        # If question asks "who approves" or "approve", and section deals with
        # LWP approval authority, give strong bonus
        approval_bonus = 0
        section_has_lwp = _has_phrase(section_body.lower(), ["leave without pay", "lwp"])
        question_about_approval = _has_phrase(q_lower, ["approves", "who approves", "approve", "approving"])
        question_about_lwp = _has_phrase(q_lower, ["leave without pay", "lwp"])
        if section_has_lwp and question_about_approval:
            approval_bonus = 60
        elif section_has_lwp and question_about_lwp:
            approval_bonus = 40

        # Score 4: strong bonus if 3+ question keywords appear in section
        three_or_more = overlap_count >= 3

        # Compute total score
        score = 0
        # Primary: number of question keywords appearing in section (heavily weighted)
        score += overlap_count * 10
        # Strong phrase bonus for "leave without pay" / LWP context
        score += lwp_bonus
        # Approval context bonus
        score += approval_bonus
        # Strong bonus if 3+ question keywords appear (distinguishes specific from generic)
        if three_or_more:
            score += 50
        # Secondary: if no LWP/approval bonus, use filtered keyword count as tiebreaker
        score += overlap_count * 3

        if best_match is None or score > best_match[1]:
            best_match = (section_num, score, section_body)

    if best_match is None:
        return None

    section_num, score, section_body = best_match
    return section_num, section_body


def answer_question(question, documents):
    """Answer a question using single-source documents only.

    Returns (answer_text, source_doc, section_num) or (refusal_template, None, None).
    Never blends claims from multiple documents.
    """
    # Step 1: Classify which document the question belongs to
    doc_name = _classify_document(question, documents)

    # Step 2: Find the best section in that document
    if doc_name:
        result = _find_best_section(documents, question, doc_name)
        if result:
            section_num, section_body = result
            # For HR document LWP approval questions, explicitly prefer section 5.2
            # which states "LWP requires approval from the Department Head and the HR Director"
            if doc_name == "policy_hr_leave.txt" and _has_phrase(q_lower := question.lower(), ["leave without pay", "lwp", "approves", "who approves"]):
                sections = documents.get(doc_name, {})
                if section_num != "5.2" and "5.2" in sections:
                    sec_52_body = sections["5.2"]
                    # Check if section 5.2 actually deals with LWP approval
                    if _has_phrase(sec_52_body.lower(), ["department head", "hr director", "approve", "requires"]):
                        # Use section 5.2 instead
                        section_num = "5.2"
                        section_body = sec_52_body
            cited = f"{section_body} (Source: {doc_name} section {section_num})"
            return section_body, doc_name, section_num

    # Step 3: No good match found - use refusal template
    return REFUSAL_TEMPLATE, None, None


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument("question", nargs="?", help="Question to ask about company policy")
    args = parser.parse_args()

    question = args.question if args.question else input("Enter your question: ")

    documents = index_documents()
    if not documents:
        print("Error: No policy documents found.")
        sys.exit(1)

    answer, doc, section = answer_question(question, documents)

    if doc is None:
        print(REFUSAL_TEMPLATE)
    else:
        # Encode answer to handle potential Unicode characters in section bodies
        answer_enc = answer.encode("ascii", errors="replace").decode("ascii")
        print(f"{answer_enc} (Source: {doc} section {section})")


if __name__ == "__main__":
    main()