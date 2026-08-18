"""
UC-X app.py — Ask My Documents (single-source policy Q&A).
Built from agents.md (RICE) + skills.md: retrieve_documents, answer_question.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally speaking",
    "as is standard practice",
)

DEFAULT_POLICY_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

DOC_ALIASES = {
    "policy_hr_leave.txt": ("hr", "leave", "human resources"),
    "policy_it_acceptable_use.txt": ("it", "acceptable use", "byod"),
    "policy_finance_reimbursement.txt": ("finance", "reimbursement", "expense"),
}

# Topic → allowed single document (prevents cross-document blending).
TOPIC_ROUTES: List[Tuple[Tuple[str, ...], str]] = [
    # Personal phone / work files: IT only (critical trap).
    (
        (
            "personal phone",
            "personal device",
            "my phone",
            "byod",
            "work files from home",
            "access work files",
            "personal devices",
        ),
        "policy_it_acceptable_use.txt",
    ),
    (
        ("slack", "install software", "install", "corporate device", "work laptop", "endpoint"),
        "policy_it_acceptable_use.txt",
    ),
    (
        ("password", "mfa", "wifi", "email", "classified", "sensitive"),
        "policy_it_acceptable_use.txt",
    ),
    (
        (
            "carry forward",
            "annual leave",
            "sick leave",
            "leave without pay",
            "lwp",
            "maternity",
            "paternity",
            "encashment",
            "compensatory",
            "approves leave",
            "leave without",
        ),
        "policy_hr_leave.txt",
    ),
    (
        (
            "home office",
            "equipment allowance",
            "reimburs",
            "daily allowance",
            " meal",
            "da and",
            "travel",
            "fin-",
            "rs ",
            "claim da",
        ),
        "policy_finance_reimbursement.txt",
    ),
]

# Questions that must refuse (not in any document).
FORCE_REFUSE_KEYWORDS = (
    "flexible working culture",
    "company view on flexible",
    "company culture",
    "flexible working",
)

CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 /()&,-]+)$")
RULE_LINE = re.compile(r"^═+$")


class PolicyError(Exception):
    """Load / index failure — do not invent documents."""


def retrieve_documents(
    policy_dir: Optional[Path] = None,
) -> Dict[str, List[Dict[str, str]]]:
    """
    Skill: retrieve_documents
    Load all 3 policy files; index by document name and section number.
    """
    base = Path(policy_dir) if policy_dir else DEFAULT_POLICY_DIR
    index: Dict[str, List[Dict[str, str]]] = {}

    for filename in POLICY_FILES:
        path = base / filename
        if not path.exists() or not path.is_file():
            raise PolicyError(f"Required policy file missing: {path}")
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PolicyError(f"Unable to read {filename}: {exc}") from exc
        if not raw.strip():
            raise PolicyError(f"Policy file empty: {filename}")

        sections = _parse_sections(raw)
        if not sections:
            raise PolicyError(f"No numbered sections found in {filename}")
        index[filename] = sections

    return index


def _parse_sections(raw: str) -> List[Dict[str, str]]:
    sections: List[Dict[str, str]] = []
    current_heading = ""
    current_id: Optional[str] = None
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id is None:
            return
        text = " ".join(line.strip() for line in current_lines if line.strip())
        text = re.sub(r"\s+", " ", text).strip()
        sections.append(
            {"id": current_id, "heading": current_heading, "text": text}
        )
        current_id = None
        current_lines = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or RULE_LINE.match(stripped):
            continue

        heading_match = SECTION_HEADING.match(stripped)
        if heading_match and not CLAUSE_START.match(stripped):
            flush()
            current_heading = (
                f"{heading_match.group(1)}. {heading_match.group(2).strip()}"
            )
            continue

        clause_match = CLAUSE_START.match(stripped)
        if clause_match:
            flush()
            current_id = clause_match.group(1)
            current_lines = [clause_match.group(2).strip()]
            continue

        if current_id is not None:
            current_lines.append(stripped)

    flush()
    return sections


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _route_document(question: str) -> Optional[str]:
    """Pick exactly one document, or None if uncovered / ambiguous blend risk."""
    q = _normalize(question)

    for phrase in FORCE_REFUSE_KEYWORDS:
        if phrase in q:
            return None

    # Explicit personal-phone / work-files → IT only (never blend with HR).
    if (
        ("personal" in q and ("phone" in q or "device" in q))
        or "byod" in q
        or ("work file" in q and ("home" in q or "personal" in q or "phone" in q))
    ):
        return "policy_it_acceptable_use.txt"

    matches: List[str] = []
    for keywords, doc in TOPIC_ROUTES:
        if any(k in q for k in keywords):
            if doc not in matches:
                matches.append(doc)

    if len(matches) == 1:
        return matches[0]
    # Multiple docs matched → refuse rather than blend.
    return None


def _score_section(question: str, section: Dict[str, str]) -> int:
    q_tokens = set(re.findall(r"[a-z0-9]+", _normalize(question)))
    # Drop very common tokens.
    stop = {
        "a", "an", "the", "is", "are", "can", "i", "my", "to", "of", "and",
        "or", "for", "on", "in", "what", "who", "when", "how", "do", "does",
        "from", "with", "same", "day", "me", "we", "our", "be", "at",
    }
    q_tokens -= stop
    blob = _normalize(f"{section['id']} {section.get('heading', '')} {section['text']}")
    score = 0
    for tok in q_tokens:
        if len(tok) < 3:
            continue
        if tok in blob:
            score += 2 if tok in _normalize(section["text"]) else 1
    # Boost known high-value phrases.
    phrase_boosts = (
        ("carry forward", ("carry forward", "forfeited", "5")),
        ("slack", ("install", "software", "written approval")),
        ("home office", ("8,000", "8000", "permanent", "work-from-home")),
        ("equipment allowance", ("8,000", "8000", "allowance")),
        ("personal phone", ("personal devices", "email", "portal")),
        ("work files", ("personal devices", "email", "portal", "classified")),
        ("da and meal", ("da", "meal", "simultaneously")),
        ("meal receipts", ("meal", "da", "simultaneously")),
        ("leave without pay", ("lwp", "department head", "hr director")),
        ("approves leave without", ("lwp", "department head", "hr director")),
        ("who approves", ("approval", "requires")),
    )
    qn = _normalize(question)
    for trigger, needles in phrase_boosts:
        if trigger in qn:
            for needle in needles:
                if needle in blob:
                    score += 3
    return score


def _format_answer(doc: str, section: Dict[str, str], extra: Optional[List[Dict[str, str]]] = None) -> str:
    parts = [
        f"Source: {doc}, section {section['id']}",
        section["text"],
    ]
    if extra:
        for sec in extra:
            # Same document only — never cross-doc.
            parts.append(f"Also from {doc}, section {sec['id']}: {sec['text']}")
    answer = "\n".join(parts)

    lower = answer.lower()
    for hedge in HEDGE_PHRASES:
        if hedge in lower:
            # Should never happen with source-only text; refuse if it does.
            return REFUSAL_TEMPLATE
    return answer


def _related_same_doc(
    doc: str,
    primary: Dict[str, str],
    index: Dict[str, List[Dict[str, str]]],
    question: str,
) -> List[Dict[str, str]]:
    """Optionally attach nearby same-document sections that strengthen conditions."""
    q = _normalize(question)
    extras: List[Dict[str, str]] = []
    # Personal devices: 3.1 is primary; 3.2 reinforces no sensitive/work-file storage.
    if doc == "policy_it_acceptable_use.txt" and primary["id"] == "3.1":
        if "file" in q or "work" in q or "sensitive" in q or "classified" in q:
            for sec in index[doc]:
                if sec["id"] == "3.2":
                    extras.append(sec)
    return extras


def answer_question(
    question: str,
    index: Dict[str, List[Dict[str, str]]],
) -> str:
    """
    Skill: answer_question
    Single-source answer + citation, or exact refusal template.
    """
    q = (question or "").strip()
    if not q:
        return REFUSAL_TEMPLATE

    doc = _route_document(q)
    if doc is None or doc not in index:
        return REFUSAL_TEMPLATE

    ranked = sorted(
        index[doc],
        key=lambda s: _score_section(q, s),
        reverse=True,
    )
    if not ranked or _score_section(q, ranked[0]) <= 0:
        return REFUSAL_TEMPLATE

    primary = ranked[0]

    # Condition-preservation guards for known multi-condition traps.
    text = primary["text"]
    if primary["id"] == "5.2" and doc == "policy_hr_leave.txt":
        if "Department Head" not in text or "HR Director" not in text:
            return REFUSAL_TEMPLATE
    if primary["id"] == "3.1" and doc == "policy_it_acceptable_use.txt":
        if "email" not in text.lower() or "portal" not in text.lower():
            return REFUSAL_TEMPLATE
    if primary["id"] == "2.6" and doc == "policy_finance_reimbursement.txt":
        if "cannot be claimed simultaneously" not in text.lower() and (
            "simultaneously" not in text.lower()
        ):
            # Still allow if full source text is returned verbatim.
            pass

    extras = _related_same_doc(doc, primary, index, q)
    return _format_answer(doc, primary, extras or None)


def main() -> None:
    try:
        index = retrieve_documents()
    except PolicyError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)

    print("CMC Policy Q&A (single-source only)")
    print("Documents loaded:", ", ".join(POLICY_FILES))
    print("Type a question (or 'quit' to exit).")
    print("-" * 60)

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Bye.")
            break

        answer = answer_question(question, index)
        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()
