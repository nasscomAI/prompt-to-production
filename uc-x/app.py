"""
UC-X — Ask My Documents

Document-grounded policy question-answering CLI.

Uses only:
- policy_hr_leave.txt
- policy_it_acceptable_use.txt
- policy_finance_reimbursement.txt

No external libraries are required.
"""

import argparse
import os
import re


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


def load_documents(base_dir):
    """
    Load all three policy documents.

    Returns:
        {
            filename: [
                {
                    "section": "2.3",
                    "text": "..."
                },
                ...
            ]
        }
    """

    documents = {}

    for filename in POLICY_FILES:
        path = os.path.join(base_dir, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Required policy document not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        documents[filename] = parse_sections(content)

    return documents


def parse_sections(content):
    """
    Parse numbered policy sections.

    Supports headings such as:
        2.3 ...
        Section 2.3 ...
    """

    lines = content.splitlines()
    sections = []

    current_section = None
    current_text = []

    section_pattern = re.compile(
        r"^\s*(?:section\s+)?(\d+(?:\.\d+)*)\s*[\.\-:]?\s*(.*)$",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        match = section_pattern.match(stripped)

        if match:
            if current_section is not None:
                sections.append({
                    "section": current_section,
                    "text": " ".join(current_text).strip(),
                })

            current_section = match.group(1)
            heading_text = match.group(2).strip()
            current_text = [heading_text] if heading_text else []

        elif current_section is not None:
            current_text.append(stripped)

    if current_section is not None:
        sections.append({
            "section": current_section,
            "text": " ".join(current_text).strip(),
        })

    return sections


def normalize(text):
    """Normalize text for simple keyword matching."""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def question_terms(question):
    """
    Extract meaningful terms from a question.
    """

    stop_words = {
        "can",
        "i",
        "we",
        "the",
        "a",
        "an",
        "is",
        "are",
        "am",
        "to",
        "of",
        "for",
        "in",
        "on",
        "and",
        "or",
        "my",
        "me",
        "what",
        "who",
        "how",
        "do",
        "does",
        "it",
        "be",
        "with",
        "from",
        "when",
        "during",
        "under",
        "about",
    }

    words = normalize(question).split()

    return [
        word
        for word in words
        if len(word) > 2 and word not in stop_words
    ]


def score_section(question, section_text):
    """
    Calculate a simple deterministic relevance score.
    """

    question_normalized = normalize(question)
    section_normalized = normalize(section_text)

    terms = question_terms(question)

    score = 0

    for term in terms:
        if term in section_normalized:
            score += 1

    # Give additional weight to exact multi-word phrases.
    important_phrases = [
        "carry forward",
        "personal phone",
        "work files",
        "home office",
        "leave without pay",
        "written approval",
        "medical certificate",
        "meal receipts",
        "da receipts",
        "slack",
        "equipment allowance",
        "flexible working",
        "annual leave",
    ]

    for phrase in important_phrases:
        if phrase in question_normalized and phrase in section_normalized:
            score += 3

    return score


def find_candidates(question, documents):
    """
    Find relevant sections.

    Returns a list of:
        (filename, section, text, score)
    """

    candidates = []

    for filename, sections in documents.items():
        for section in sections:
            score = score_section(question, section["text"])

            if score > 0:
                candidates.append(
                    (
                        filename,
                        section["section"],
                        section["text"],
                        score,
                    )
                )

    candidates.sort(key=lambda item: item[3], reverse=True)

    return candidates


def contains_cross_document_conflict(question, candidates):
    """
    Detect situations where multiple policy documents appear equally
    relevant and combining them could create a new policy meaning.
    """

    if len(candidates) < 2:
        return False

    top_score = candidates[0][3]

    top_documents = {
        candidate[0]
        for candidate in candidates
        if candidate[3] == top_score
    }

    return len(top_documents) > 1


def contains_hedging(answer):
    """Check for prohibited hedging language."""

    lowered = answer.lower()

    return any(
        phrase in lowered
        for phrase in HEDGING_PHRASES
    )


def build_answer(question, candidate):
    """
    Build an answer from exactly one policy section.
    """

    filename, section, text, _ = candidate

    answer = (
        f"According to {filename}, Section {section}: "
        f"{text}"
    )

    if contains_hedging(answer):
        return REFUSAL_TEMPLATE

    return answer


def answer_question(question, documents):
    """
    Answer a question using a single policy document only.

    Unsupported or cross-document questions receive the exact
    refusal template.
    """

    question = question.strip()

    if not question:
        return REFUSAL_TEMPLATE

    candidates = find_candidates(question, documents)

    if not candidates:
        return REFUSAL_TEMPLATE

    if contains_cross_document_conflict(question, candidates):
        return REFUSAL_TEMPLATE

    best = candidates[0]

    # Require enough direct evidence before answering.
    if best[3] < 2:
        return REFUSAL_TEMPLATE

    return build_answer(question, best)


def main():
    parser = argparse.ArgumentParser(
        description="UC-X — Ask My Documents"
    )

    parser.add_argument(
        "--policy-dir",
        default="../data/policy-documents",
        help="Directory containing the three policy documents.",
    )

    args = parser.parse_args()

    try:
        documents = load_documents(args.policy_dir)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: Unable to load policy documents: {exc}")
        return

    print("UC-X — Ask My Documents")
    print("Policy documents loaded successfully.")
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        answer = answer_question(
            question,
            documents,
        )

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()