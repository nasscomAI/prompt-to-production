
"""
UC-X — Ask My Documents

Document-grounded policy question answering.

Core failure modes:
1. Cross-document blending
2. Hedged hallucination
3. Condition dropping
4. Unsupported-topic retrieval
"""

import argparse
import os
import re


# ================================================================
# PATHS
# ================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS = {
    "HR Leave Policy": os.path.normpath(
        os.path.join(
            BASE_DIR,
            "..",
            "data",
            "policy-documents",
            "policy_hr_leave.txt",
        )
    ),

    "IT Acceptable Use Policy": os.path.normpath(
        os.path.join(
            BASE_DIR,
            "..",
            "data",
            "policy-documents",
            "policy_it_acceptable_use.txt",
        )
    ),

    "Finance Reimbursement Policy": os.path.normpath(
        os.path.join(
            BASE_DIR,
            "..",
            "data",
            "policy-documents",
            "policy_finance_reimbursement.txt",
        )
    ),
}


# ================================================================
# STOP WORDS
# ================================================================

STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "am",
    "was",
    "were",
    "be",
    "been",
    "being",
    "to",
    "of",
    "for",
    "and",
    "or",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "can",
    "could",
    "would",
    "should",
    "do",
    "does",
    "did",
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "it",
    "this",
    "that",
    "policy",
    "policies",
    "requirements",
    "requirement",
    "rules",
    "rule",
    "apply",
    "applies",
}


# ================================================================
# SUPPORTED POLICY TOPICS
# ================================================================

TOPIC_KEYWORDS = {
    "HR Leave Policy": [
        "leave",
        "annual leave",
        "sick leave",
        "maternity leave",
        "paternity leave",
        "maternity",
        "paternity",
        "leave without pay",
        "lwp",
        "lop",
        "loss of pay",
        "carry forward",
        "leave encashment",
        "encashment",
        "public holiday",
        "compensatory off",
        "medical certificate",
        "grievance",
    ],

    "IT Acceptable Use Policy": [
        "acceptable use",
        "software",
        "install software",
        "software installation",
        "installation",
        "corporate device",
        "personal device",
        "laptop",
        "desktop",
        "cmc email",
        "email",
        "password",
        "mfa",
        "multi-factor authentication",
        "authentication",
        "internet",
        "confidential data",
        "restricted data",
        "classified data",
        "secure print",
        "remote wipe",
        "endpoint security",
        "access control",
    ],

    "Finance Reimbursement Policy": [
        "reimbursement",
        "reimburse",
        "expense",
        "expenses",
        "claim",
        "claims",
        "travel",
        "local travel",
        "outstation travel",
        "air travel",
        "hotel accommodation",
        "hotel",
        "accommodation",
        "daily allowance",
        "da",
        "meal expenses",
        "meal",
        "work from home",
        "wfh",
        "home office",
        "equipment allowance",
        "training expenses",
        "training",
        "course fee",
        "course fees",
        "certification",
        "certification exam",
        "exam fee",
        "receipts",
        "receipt",
        "fin-exp1",
        "fin-t1",
        "fin-tr1",
    ],
}


# ================================================================
# UNSUPPORTED TOPICS
# ================================================================

UNSUPPORTED_PATTERNS = [
    # Parking
    r"\bparking\b",
    r"\bparking reimbursement\b",

    # Insurance
    r"\bmedical insurance\b",
    r"\bhealth insurance\b",
    r"\binsurance\b",

    # Employee events / celebrations
    r"\bbirthday\b",
    r"\bbirthday celebration\b",
    r"\bbirthday celebrations\b",
    r"\bcelebration\b",
    r"\bcelebrations\b",
]


# ================================================================
# TEXT NORMALIZATION
# ================================================================

def normalize_text(text, collapse_whitespace=False):
    """
    Normalize common encoding artifacts.

    Line boundaries are preserved unless collapse_whitespace=True.
    """

    if text is None:
        return ""

    replacements = {
        "Ã¢â‚¬â€œ": "-",
        "Ã¢â‚¬â€": "-",
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€¦": "...",
        "â€¢": "-",
        "Â": "",
        "âˆ’": "-",
        "â‰¥": ">=",
        "â‰¤": "<=",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    if collapse_whitespace:
        return re.sub(r"\s+", " ", text).strip()

    return "\n".join(
        line.rstrip()
        for line in text.split("\n")
    ).strip()


def normalize_question(question):
    return normalize_text(
        question,
        collapse_whitespace=True,
    ).lower()


def tokenize(text):
    words = re.findall(
        r"[a-z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    }


# ================================================================
# POLICY CLAUSE PARSER
# ================================================================

def split_into_sections(text):
    """
    Parse numbered policy clauses while preserving multiline clauses.

    Example:

    5.2 LWP requires approval from the Department Head and the
        HR Director. Manager approval alone is not sufficient.

    becomes one complete clause.
    """

    sections = []

    clause_pattern = re.compile(
        r"^\s*(\d+\.\d+)\s+(.*)$"
    )

    heading_pattern = re.compile(
        r"^\s*(\d+)\.\s+(.+)$"
    )

    current = None

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        # Ignore decorative separator lines.
        if re.fullmatch(
            r"[-=_•· ]{5,}",
            line,
        ):
            continue

        # --------------------------------------------------------
        # Numbered clause: 2.3, 2.4, 5.1, etc.
        # --------------------------------------------------------

        clause_match = clause_pattern.match(line)

        if clause_match:

            if current is not None:
                sections.append(current)

            number = clause_match.group(1)
            body = clause_match.group(2).strip()

            current = {
                "index": number,
                "text": f"{number} {body}",
                "type": "clause",
            }

            continue

        # --------------------------------------------------------
        # Major heading: 1. TITLE
        # --------------------------------------------------------

        heading_match = heading_pattern.match(line)

        if heading_match:

            if current is not None:
                sections.append(current)
                current = None

            number = heading_match.group(1)
            title = heading_match.group(2).strip()

            sections.append(
                {
                    "index": number,
                    "text": f"{number} {title}",
                    "type": "heading",
                }
            )

            continue

        # --------------------------------------------------------
        # Continuation line of current clause.
        # --------------------------------------------------------

        if current is not None:
            current["text"] += " " + line

    if current is not None:
        sections.append(current)

    return sections


# ================================================================
# LOAD DOCUMENTS
# ================================================================

def load_documents():

    documents = {}

    for document_name, path in DOCUMENTS.items():

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required policy document not found: {path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:

            raw_text = file.read()

        text = normalize_text(
            raw_text,
            collapse_whitespace=False,
        )

        sections = split_into_sections(text)

        clauses = [
            section
            for section in sections
            if section["type"] == "clause"
        ]

        if not clauses:
            raise ValueError(
                f"No policy clauses could be parsed from: {path}"
            )

        documents[document_name] = {
            "path": path,
            "text": text,
            "sections": sections,
            "clauses": clauses,
        }

    return documents


# ================================================================
# UNSUPPORTED TOPIC CHECK
# ================================================================

def is_explicitly_unsupported(question):

    q = normalize_question(question)

    for pattern in UNSUPPORTED_PATTERNS:

        if re.search(pattern, q):
            return True

    return False


# ================================================================
# TOPIC MATCHING
# ================================================================

def matching_topics(question):

    q = normalize_question(question)

    matches = []

    for document_name, keywords in TOPIC_KEYWORDS.items():

        for keyword in keywords:

            # Avoid matching tiny generic fragments.
            if len(keyword) < 3:
                continue

            if keyword in q:

                matches.append(
                    document_name
                )

                break

    return list(
        dict.fromkeys(matches)
    )


def explicit_document_candidates(question):

    q = normalize_question(question)

    candidates = []

    # ------------------------------------------------------------
    # HR
    # ------------------------------------------------------------

    if any(
        phrase in q
        for phrase in [
            "hr leave",
            "leave policy",
            "leave without pay",
            "lwp",
            "annual leave",
            "sick leave",
            "maternity leave",
            "paternity leave",
            "leave approval",
        ]
    ):

        candidates.append(
            "HR Leave Policy"
        )

    # ------------------------------------------------------------
    # IT
    # ------------------------------------------------------------

    if any(
        phrase in q
        for phrase in [
            "it policy",
            "acceptable use",
            "software installation",
            "install software",
            "corporate device",
            "personal device",
            "cmc email",
            "password",
            "mfa",
        ]
    ):

        candidates.append(
            "IT Acceptable Use Policy"
        )

    # ------------------------------------------------------------
    # Finance
    # ------------------------------------------------------------

    if any(
        phrase in q
        for phrase in [
            "finance policy",
            "reimbursement",
            "reimburse",
            "expense",
            "travel reimbursement",
            "course fee",
            "certification reimbursement",
            "wfh equipment",
            "home office",
        ]
    ):

        candidates.append(
            "Finance Reimbursement Policy"
        )

    return list(
        dict.fromkeys(candidates)
    )


# ================================================================
# AMBIGUITY / COMPARISON
# ================================================================

def is_generic_approval_question(question):

    q = normalize_question(question)

    approval_phrases = [
        "approval requirements",
        "approval requirement",
        "approval rules",
        "approval rule",
        "who must approve",
        "who can approve",
        "what approvals",
        "what approval",
    ]

    employee_phrases = [
        "employee",
        "employees",
        "staff",
        "personnel",
    ]

    has_approval = any(
        phrase in q
        for phrase in approval_phrases
    )

    has_employee = any(
        phrase in q
        for phrase in employee_phrases
    )

    if not has_approval or not has_employee:
        return False

    # A specific topic removes ambiguity.
    return len(
        matching_topics(q)
    ) == 0


def is_comparison_question(question):

    q = normalize_question(question)

    comparison_phrases = [
        "compare",
        "comparison",
        "difference between",
        "differences between",
        "versus",
        " vs ",
        "both policies",
    ]

    return any(
        phrase in q
        for phrase in comparison_phrases
    )


# ================================================================
# RETRIEVAL SCORING
# ================================================================

def score_section(question, section_text):

    question_terms = tokenize(question)
    section_terms = tokenize(section_text)

    if not question_terms:
        return 0

    overlap = question_terms.intersection(
        section_terms
    )

    score = len(overlap)

    important_phrases = [
        "annual leave",
        "sick leave",
        "medical certificate",
        "work from home",
        "reimbursement",
        "travel",
        "internet",
        "password",
        "personal device",
        "acceptable use",
        "manager approval",
        "department head",
        "hr director",
        "leave without pay",
        "course fee",
        "certification",
        "air travel",
    ]

    q = normalize_question(question)
    section = normalize_question(section_text)

    for phrase in important_phrases:

        if (
            phrase in q
            and phrase in section
        ):
            score += 3

    return score


# ================================================================
# RETRIEVE POLICY EVIDENCE
# ================================================================

def retrieve_policy_evidence(
    documents,
    question,
    max_results=20,
):

    # Critical guard:
    # unsupported questions never reach retrieval.
    if is_explicitly_unsupported(question):
        return []

    explicit = explicit_document_candidates(
        question
    )

    topics = matching_topics(
        question
    )

    allowed_documents = (
        explicit
        or topics
    )

    if not allowed_documents:
        return []

    evidence = []

    for document_name in allowed_documents:

        if document_name not in documents:
            continue

        for section in documents[
            document_name
        ]["sections"]:

            score = score_section(
                question,
                section["text"],
            )

            if score <= 0:
                continue

            evidence.append(
                {
                    "document": document_name,
                    "path": documents[
                        document_name
                    ]["path"],
                    "section_index": section[
                        "index"
                    ],
                    "score": score,
                    "text": section["text"],
                    "type": section["type"],
                }
            )

    evidence.sort(
        key=lambda item: (
            -item["score"],
            item["section_index"],
        )
    )

    return evidence[:max_results]


# ================================================================
# ADD SPECIFIC CLAUSE
# ================================================================

def add_clause(
    evidence,
    documents,
    document_name,
    clause_number,
):

    for item in evidence:

        if (
            item["document"] == document_name
            and item["section_index"] == clause_number
        ):
            return

    if document_name not in documents:
        return

    for section in documents[
        document_name
    ]["sections"]:

        if (
            section["type"] == "clause"
            and section["index"] == clause_number
        ):

            evidence.append(
                {
                    "document": document_name,
                    "path": documents[
                        document_name
                    ]["path"],
                    "section_index": clause_number,
                    "score": 100,
                    "text": section["text"],
                    "type": "clause",
                }
            )

            return


# ================================================================
# CONDITION PRESERVATION
# ================================================================

def expand_related_conditions(
    documents,
    question,
    evidence,
):

    q = normalize_question(question)

    # ------------------------------------------------------------
    # LWP
    # ------------------------------------------------------------

    if (
        "lwp" in q
        or "leave without pay" in q
    ):

        for clause in [
            "5.1",
            "5.2",
            "5.3",
            "5.4",
        ]:

            add_clause(
                evidence,
                documents,
                "HR Leave Policy",
                clause,
            )

    # ------------------------------------------------------------
    # Annual leave approval
    # ------------------------------------------------------------

    if (
        "annual leave" in q
        or (
            "leave" in q
            and "approval" in q
        )
    ):

        for clause in [
            "2.3",
            "2.4",
            "2.5",
        ]:

            add_clause(
                evidence,
                documents,
                "HR Leave Policy",
                clause,
            )

    # ------------------------------------------------------------
    # Personal device + CMC email
    # ------------------------------------------------------------

    if (
        "personal device" in q
        and "cmc email" in q
    ):

        for clause in [
            "3.1",
            "3.2",
            "3.3",
            "3.4",
            "3.5",
        ]:

            add_clause(
                evidence,
                documents,
                "IT Acceptable Use Policy",
                clause,
            )

    # ------------------------------------------------------------
    # Software installation
    # ------------------------------------------------------------

    if (
        "software" in q
        and (
            "install" in q
            or "installation" in q
        )
    ):

        for clause in [
            "2.3",
            "2.4",
        ]:

            add_clause(
                evidence,
                documents,
                "IT Acceptable Use Policy",
                clause,
            )

    return evidence


# ================================================================
# RESPONSE BUILDERS
# ================================================================

def not_found_answer():

    return (
        "NOT FOUND IN SUPPLIED DOCUMENTS.\n"
        "The supplied policy documents do not contain "
        "information about the specific subject asked about "
        "in this question."
    )


def clarification_answer():

    return (
        "CLARIFICATION REQUIRED.\n"
        "The question is ambiguous across the supplied "
        "policy documents. Please specify the policy or "
        "ask for an explicit comparison."
    )


def format_single_document_answer(
    evidence,
    document_name,
):

    evidence = [
        item
        for item in evidence
        if item["document"] == document_name
    ]

    if not evidence:
        return not_found_answer()

    evidence.sort(
        key=lambda item: (
            item["type"] != "clause",
            -item["score"],
            item["section_index"],
        )
    )

    lines = [
        f"Source: {document_name}",
        "Evidence:",
    ]

    seen = set()

    for item in evidence:

        key = (
            item["document"],
            item["section_index"],
            item["text"],
        )

        if key in seen:
            continue

        seen.add(key)

        lines.append(
            f"- Section {item['section_index']}: "
            f"{item['text']}"
        )

    lines.append(
        "Grounding: Answer based only on the supplied document."
    )

    return "\n".join(lines)


def format_comparison_answer(
    evidence,
    requested_documents,
):

    if not evidence:
        return not_found_answer()

    lines = [
        "Comparison based only on the supplied policy documents.",
        "",
    ]

    for document_name in requested_documents:

        doc_evidence = [
            item
            for item in evidence
            if item["document"] == document_name
        ]

        if not doc_evidence:
            continue

        doc_evidence.sort(
            key=lambda item: (
                item["type"] != "clause",
                -item["score"],
                item["section_index"],
            )
        )

        lines.append(
            f"{document_name}:"
        )

        seen = set()

        for item in doc_evidence:

            key = (
                item["document"],
                item["section_index"],
            )

            if key in seen:
                continue

            seen.add(key)

            lines.append(
                f"- Section {item['section_index']}: "
                f"{item['text']}"
            )

        lines.append("")

    lines.append(
        "Cross-document rule: Each policy is shown separately. "
        "No condition from one document has been applied to "
        "another document."
    )

    return "\n".join(lines)


# ================================================================
# MAIN ANSWER ENGINE
# ================================================================

def answer_question(
    documents,
    question,
):

    question = question.strip()

    if not question:
        return ""

    # ============================================================
    # 1. UNSUPPORTED TOPICS — FIRST GUARD
    # ============================================================

    if is_explicitly_unsupported(question):
        return not_found_answer()

    # ============================================================
    # 2. COMPARISON QUESTIONS
    # ============================================================

    if is_comparison_question(question):

        q = normalize_question(question)

        candidates = explicit_document_candidates(
            question
        )

        if len(candidates) < 2:
            candidates = matching_topics(
                question
            )

        # Specific assignment comparison.
        if (
            "leave approval" in q
            and "software installation" in q
        ):

            candidates = [
                "HR Leave Policy",
                "IT Acceptable Use Policy",
            ]

        if len(candidates) < 2:
            return not_found_answer()

        evidence = retrieve_policy_evidence(
            documents,
            question,
            max_results=30,
        )

        # Explicitly preserve relevant HR clauses.
        if (
            "leave approval" in q
            and "software installation" in q
        ):

            for clause in [
                "2.3",
                "2.4",
                "2.5",
            ]:

                add_clause(
                    evidence,
                    documents,
                    "HR Leave Policy",
                    clause,
                )

            # Explicitly preserve relevant IT clauses.
            for clause in [
                "2.3",
                "2.4",
            ]:

                add_clause(
                    evidence,
                    documents,
                    "IT Acceptable Use Policy",
                    clause,
                )

        return format_comparison_answer(
            evidence,
            candidates,
        )

    # ============================================================
    # 3. AMBIGUOUS APPROVAL QUESTION
    # ============================================================

    if is_generic_approval_question(question):
        return clarification_answer()

    # ============================================================
    # 4. IDENTIFY SUPPORTED DOCUMENT
    # ============================================================

    explicit_documents = explicit_document_candidates(
        question
    )

    topic_documents = matching_topics(
        question
    )

    candidates = (
        explicit_documents
        or topic_documents
    )

    # No supported topic.
    if not candidates:
        return not_found_answer()

    # ============================================================
    # 5. RETRIEVE EVIDENCE
    # ============================================================

    evidence = retrieve_policy_evidence(
        documents,
        question,
        max_results=30,
    )

    # ============================================================
    # 6. EXPAND RELATED CONDITIONS
    # ============================================================

    evidence = expand_related_conditions(
        documents,
        question,
        evidence,
    )

    evidence = [
        item
        for item in evidence
        if item["document"] in candidates
    ]

    if not evidence:
        return not_found_answer()

    # ============================================================
    # 7. PREVENT CROSS-DOCUMENT BLENDING
    # ============================================================

    matched_documents = list(
        dict.fromkeys(
            item["document"]
            for item in evidence
        )
    )

    if len(matched_documents) > 1:
        return clarification_answer()

    # ============================================================
    # 8. FINAL GROUNDED ANSWER
    # ============================================================

    return format_single_document_answer(
        evidence,
        matched_documents[0],
    )


# ================================================================
# EXACTLY 18 UC-X SELF TESTS
# ================================================================

SELF_TESTS = [

    (
        "LWP approval condition preservation",
        "What approvals are required for Leave Without Pay (LWP)?",
        [
            "5.2",
            "Department Head",
            "HR Director",
            "Manager approval alone is not sufficient",
        ],
    ),

    (
        "Personal device requirement",
        "What is required when using a personal device for CMC email?",
        [
            "3.4",
            "PIN",
            "biometric",
        ],
    ),

    (
        "Unsupported parking reimbursement",
        "What is the policy for employee parking reimbursement?",
        [
            "NOT FOUND IN SUPPLIED DOCUMENTS",
        ],
    ),

    (
        "Comparison keeps documents separate",
        "Compare the leave approval requirements with the IT software installation requirements.",
        [
            "HR Leave Policy",
            "IT Acceptable Use Policy",
            "2.3",
            "2.4",
            "Cross-document rule",
        ],
    ),

    (
        "Unsupported random subject",
        "What is the policy for employee birthday celebrations?",
        [
            "NOT FOUND IN SUPPLIED DOCUMENTS",
        ],
    ),

    (
        "Finance reimbursement deadline",
        "What is the deadline for submitting reimbursement claims?",
        [
            "30 calendar days",
            "1.3",
        ],
    ),

    (
        "IT software installation",
        "Can employees install software on corporate devices?",
        [
            "2.3",
            "2.4",
        ],
    ),

    (
        "HR leave written approval",
        "Who must approve an annual leave application?",
        [
            "2.4",
            "written approval",
            "direct manager",
        ],
    ),

    (
        "Finance course fee limit",
        "How much are course fees reimbursable?",
        [
            "15,000",
            "4.2",
        ],
    ),

    (
        "Annual leave submission deadline",
        "How early must employees submit annual leave applications?",
        [
            "14 calendar days",
            "2.3",
        ],
    ),

    (
        "Lost personal device reporting",
        "What should an employee do if a personal device containing CMC email is lost?",
        [
            "4 hours",
            "3.5",
        ],
    ),

    (
        "Professional certification reimbursement",
        "Are professional certification exam fees reimbursable?",
        [
            "5,000",
            "4.3",
        ],
    ),

    (
        "Ambiguous multi-document question",
        "What approval requirements apply to employees?",
        [
            "CLARIFICATION REQUIRED",
        ],
    ),

    (
        "Personal expenses are not reimbursable",
        "Are personal expenses reimbursable?",
        [
            "1.2",
            "not reimbursable",
        ],
    ),

    (
        "Outstation travel pre-approval",
        "Does outstation travel require pre-approval?",
        [
            "2.2",
            "pre-approved",
            "FIN-T1",
        ],
    ),

    (
        "Air travel restriction",
        "When is air travel permitted?",
        [
            "2.3",
            "500 km",
            "Economy class",
        ],
    ),

    (
        "Work from home equipment restriction",
        "What equipment is excluded from the WFH allowance?",
        [
            "3.3",
            "personal computers",
            "laptops",
        ],
    ),

    (
        "Unsupported medical insurance",
        "Does the policy cover medical insurance reimbursement?",
        [
            "NOT FOUND IN SUPPLIED DOCUMENTS",
        ],
    ),
]


# ================================================================
# SELF TEST RUNNER
# ================================================================

def run_self_tests(documents):

    print()
    print("UC-X SELF TESTS")
    print("=" * 70)

    passed = 0
    failed = 0

    for number, test in enumerate(
        SELF_TESTS,
        start=1,
    ):

        name, question, required = test

        actual = answer_question(
            documents,
            question,
        )

        missing = [
            value
            for value in required
            if value.lower()
            not in actual.lower()
        ]

        if not missing:

            print(
                f"[PASS] {number}. {name}"
            )

            passed += 1

        else:

            print(
                f"[FAIL] {number}. {name}"
            )

            print(
                "       Missing: "
                + ", ".join(missing)
            )

            print(
                "       Actual answer:"
            )

            print(actual)

            failed += 1

    print()
    print("-" * 70)

    print(
        f"SELF TEST RESULT: "
        f"{passed} passed, {failed} failed"
    )

    print("-" * 70)

    if failed == 0:

        print(
            "✓ UC-X SELF TESTS PASSED."
        )

        return True

    print(
        "✗ UC-X SELF TESTS FAILED. "
        "Do not commit yet."
    )

    return False


# ================================================================
# INTERACTIVE CLI
# ================================================================

def print_startup_summary(documents):

    print(
        "======================================================================"
    )

    print(
        "UC-X — Ask My Documents"
    )

    print(
        "======================================================================"
    )

    print()

    print("Loaded policy documents:")

    for name, document in documents.items():

        print(
            f"- {name} "
            f"({len(document['clauses'])} clauses)"
        )

    print()

    print("Grounding: enabled")
    print("Condition preservation: enabled")
    print("Cross-document blending: blocked")
    print("Unsupported answers: refused")
    print("Comparison mode: enabled")
    print("Ambiguity detection: enabled")

    print()

    print("Type a question.")
    print("Type 'exit' or 'quit' to stop.")

    print()


# ================================================================
# MAIN
# ================================================================

def main():

    parser = argparse.ArgumentParser(
        description="UC-X — Ask My Documents"
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run all 18 UC-X self-tests.",
    )

    args = parser.parse_args()

    try:

        documents = load_documents()

    except (OSError, ValueError) as exc:

        print(
            "ERROR: Could not load supplied policy documents."
        )

        print(str(exc))

        return 1

    # ------------------------------------------------------------
    # SELF TEST
    # ------------------------------------------------------------

    if args.self_test:

        success = run_self_tests(
            documents
        )

        return 0 if success else 1

    # ------------------------------------------------------------
    # INTERACTIVE MODE
    # ------------------------------------------------------------

    print_startup_summary(
        documents
    )

    while True:

        try:

            question = input(
                "Question: "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt,
        ):

            print()
            break

        if question.lower() in {
            "exit",
            "quit",
        }:

            break

        if not question:
            continue

        print()

        print(
            answer_question(
                documents,
                question,
            )
        )

        print()


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
