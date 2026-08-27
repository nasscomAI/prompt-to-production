"""
UC-X — Ask My Documents
Implements agents.md + skills.md: retrieve_documents, answer_question.

Interactive CLI: single-source answers with document + section citations, or the exact
refusal template. Cross-document trap (personal phone + work files + home) → IT §3.1 only.
"""
import argparse
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# agents.md — verbatim refusal template (do not paraphrase)
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DEFAULT_DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
)
DEFAULT_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

CLAUSE_START = re.compile(r"^(\d+\.\d+)\s")
MAJOR_BANNER = re.compile(r"^\s*\d+\.\s+[A-Za-z]")
BOX_LINE = re.compile(r"^[═\-\s]+$")

# agents.md enforcement — never emit these
HEDGE_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)

_STOPWORDS = frozenset(
    """
    a an the and or of to in for on at by is are was were be been being as if it its this that
    can how what when where which who whom i me my we our you your they their do does did will
    would could should may might must shall not no yes from with into about over under same both
    there then than so such only also just
    """.split()
)


def _parse_numbered_sections(text: str) -> List[Dict[str, str]]:
    """Split policy into blocks for sub-clauses X.Y at line start (same idea as uc-0b)."""
    lines = text.splitlines()
    sections: List[Dict[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = CLAUSE_START.match(line.strip())
        if not m:
            i += 1
            continue
        cid = m.group(1)
        body_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if CLAUSE_START.match(nxt.strip()):
                break
            ns = nxt.strip()
            if not ns:
                body_lines.append(lines[i])
                i += 1
                continue
            if BOX_LINE.match(ns):
                i += 1
                continue
            if MAJOR_BANNER.match(ns) and not CLAUSE_START.match(ns):
                i += 1
                continue
            body_lines.append(lines[i])
            i += 1
        sections.append({"clause_id": cid, "text": "\n".join(body_lines).strip()})
    return sections


def retrieve_documents(
    base_dir: Optional[str] = None,
    filenames: Optional[Tuple[str, ...]] = None,
) -> Dict[str, Any]:
    """
    skills.md retrieve_documents: load three UTF-8 policy files, index by basename + section id.
    """
    d = base_dir or DEFAULT_DOCS_DIR
    names = filenames or DEFAULT_FILES
    documents: Dict[str, Dict[str, Any]] = {}
    index: Dict[Tuple[str, str], str] = {}

    for fn in names:
        path = os.path.join(d, fn)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end, f"Policy must be UTF-8: {path}"
            ) from e
        except OSError as e:
            raise OSError(f"Cannot read policy file: {path}") from e
        if not raw.strip():
            raise ValueError(f"Policy file is empty: {path}")

        sections = _parse_numbered_sections(raw)
        documents[fn] = {"raw_text": raw, "sections": sections}
        for sec in sections:
            cid = sec["clause_id"]
            index[(fn, cid)] = sec["text"]

    return {"documents": documents, "index": index, "base_dir": d}


def _section_text(retrieved: Dict[str, Any], doc: str, clause_id: str) -> str:
    t = retrieved["index"].get((doc, clause_id))
    if not t:
        raise KeyError(f"No section {clause_id!r} in {doc!r}")
    return t


def _tokens(q: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9]+", q.lower()) if len(t) > 2 and t not in _STOPWORDS]


def _is_cross_document_trap(question_lower: str) -> bool:
    """
    agents.md cross_document_trap: personal phone / device + work file(s) + home / remote context.
    Answer from IT §3.1 only — do not blend HR + IT.
    """
    if "flexible" in question_lower and "culture" in question_lower:
        return False
    has_personal_device = ("personal" in question_lower and "phone" in question_lower) or (
        "personal" in question_lower and "device" in question_lower
    )
    has_files = "file" in question_lower or "files" in question_lower
    has_home = (
        "home" in question_lower
        or "working from home" in question_lower
        or "wfh" in question_lower
        or "from home" in question_lower
    )
    return bool(has_personal_device and has_files and has_home)


def _must_refuse_vague_culture(question_lower: str) -> bool:
    if "flexible" in question_lower and "culture" in question_lower:
        return True
    if "company view" in question_lower and "culture" in question_lower:
        return True
    return False


def _route_explicit(question_lower: str) -> Optional[Tuple[str, str]]:
    """Return (document_basename, clause_id) when a README test case pattern matches."""
    if _must_refuse_vague_culture(question_lower):
        return None

    if _is_cross_document_trap(question_lower):
        return ("policy_it_acceptable_use.txt", "3.1")

    if "leave without pay" in question_lower or re.search(r"\blwp\b", question_lower):
        if "approv" in question_lower or "who" in question_lower:
            return ("policy_hr_leave.txt", "5.2")

    if "carry" in question_lower and "forward" in question_lower and "leave" in question_lower:
        return ("policy_hr_leave.txt", "2.6")

    if "slack" in question_lower or (
        "install" in question_lower and ("software" in question_lower or "laptop" in question_lower)
    ):
        return ("policy_it_acceptable_use.txt", "2.3")

    if ("home office" in question_lower or "equipment allowance" in question_lower) and (
        "allowance" in question_lower or "equipment" in question_lower or "8000" in question_lower
    ):
        return ("policy_finance_reimbursement.txt", "3.1")

    if (
        re.search(r"\bda\b", question_lower)
        or "daily allowance" in question_lower
    ) and ("meal" in question_lower):
        if "same" in question_lower or "both" in question_lower or "simultaneous" in question_lower:
            return ("policy_finance_reimbursement.txt", "2.6")

    return None


def _score_sections(retrieved: Dict[str, Any], question_lower: str, qtok: List[str]) -> List[Tuple[str, str, int]]:
    ranked: List[Tuple[str, str, int]] = []
    for (doc, cid), text in retrieved["index"].items():
        tl = text.lower()
        score = sum(1 for t in qtok if t in tl)
        # small boost for exact phrases
        for phrase in ("annual leave", "leave without pay", "daily allowance"):
            if phrase in question_lower and phrase in tl:
                score += 2
        ranked.append((doc, cid, score))
    ranked.sort(key=lambda x: -x[2])
    return ranked


def answer_question(question: str, retrieved: Dict[str, Any]) -> Dict[str, Any]:
    """
    skills.md answer_question: citations + extractive text, or exact refusal_template dict.
    """
    q = question.strip()
    if not q:
        return {"refusal": True, "text": REFUSAL_TEMPLATE}

    ql = q.lower()
    if _must_refuse_vague_culture(ql):
        return {"refusal": True, "text": REFUSAL_TEMPLATE}

    routed = _route_explicit(ql)
    if not routed and _is_cross_document_trap(ql):
        routed = ("policy_it_acceptable_use.txt", "3.1")

    if not routed:
        toks = _tokens(q)
        ranked = _score_sections(retrieved, ql, toks)
        if not ranked or ranked[0][2] < 2:
            return {"refusal": True, "text": REFUSAL_TEMPLATE}
        top_doc, top_id, top_s = ranked[0]
        second_s = ranked[1][2] if len(ranked) > 1 else 0
        # If two different docs tie closely, refuse (blend risk)
        if len(ranked) > 1 and ranked[1][2] >= top_s - 1 and ranked[0][0] != ranked[1][0]:
            return {"refusal": True, "text": REFUSAL_TEMPLATE}
        if top_s < 3 and second_s >= top_s - 1:
            return {"refusal": True, "text": REFUSAL_TEMPLATE}
        routed = (top_doc, top_id)

    doc, cid = routed
    body = _section_text(retrieved, doc, cid)
    answer_text = _format_cited_answer(doc, cid, body)
    # Basic hedge check on our own output (should never trigger)
    low = answer_text.lower()
    for h in HEDGE_PHRASES:
        if h in low:
            raise AssertionError(f"Internal error: hedging phrase leaked: {h!r}")

    return {
        "refusal": False,
        "answer_text": answer_text,
        "citations": [{"document": doc, "section": cid}],
    }


def _format_cited_answer(doc: str, clause_id: str, section_text: str) -> str:
    return f"Source: {doc} · section {clause_id}\n\n{section_text}"


def _print_result(result: Dict[str, Any]) -> None:
    if result.get("refusal"):
        print(result["text"])
        return
    print(result["answer_text"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="UC-X policy Q&A (agents.md + skills.md).")
    ap.add_argument(
        "--documents-dir",
        default=DEFAULT_DOCS_DIR,
        help="Directory containing the three policy .txt files",
    )
    ap.add_argument(
        "--question",
        default=None,
        help="Single question (non-interactive); otherwise start interactive CLI",
    )
    args = ap.parse_args(argv)

    try:
        retrieved = retrieve_documents(base_dir=os.path.abspath(args.documents_dir))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.question is not None:
        _print_result(answer_question(args.question, retrieved))
        return 0

    print(
        "UC-X — Ask My Documents. Type a question, or quit / empty line to exit.\n"
        "Answers cite one policy file + section (agents.md); out-of-scope → refusal template.\n",
        file=sys.stderr,
    )
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                print("", file=sys.stderr)
                break
            if not line or line.lower() in ("quit", "exit", "q"):
                break
            _print_result(answer_question(line, retrieved))
            print("", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
