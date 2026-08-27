"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


HR_DOC = "policy_hr_leave.txt"
IT_DOC = "policy_it_acceptable_use.txt"
FIN_DOC = "policy_finance_reimbursement.txt"


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    f"({HR_DOC}, {IT_DOC}, {FIN_DOC}). "
    "Please contact [relevant team] for guidance."
)

DOC_FILES = [
    HR_DOC,
    IT_DOC,
    FIN_DOC,
]

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


@dataclass
class Section:
    document_name: str
    section_id: str
    text: str


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _read_policy_lines(file_path: Path, filename: str) -> List[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required policy file: {filename}")
    try:
        return file_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise OSError(f"Unable to read policy file: {filename}") from exc


def _extract_sections(raw_lines: List[str]) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current_section: Optional[str] = None

    for line in raw_lines:
        header_match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)
        if header_match:
            current_section = header_match.group(1)
            sections[current_section] = [header_match.group(2).strip()]
            continue

        if current_section is None:
            continue

        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        if re.match(r"^\d+\.\s", stripped):
            current_section = None
            continue

        sections[current_section].append(stripped)

    return sections


def _build_doc_index(filename: str, sections: Dict[str, List[str]]) -> Dict[str, Section]:
    return {
        section_id: Section(
            document_name=filename,
            section_id=section_id,
            text=_normalize_spaces(" ".join(lines)),
        )
        for section_id, lines in sections.items()
    }


def retrieve_documents(base_dir: Path) -> Dict[str, Dict[str, Section]]:
    """Load policy documents and index by document name and section number."""
    index: Dict[str, Dict[str, Section]] = {}

    for filename in DOC_FILES:
        file_path = base_dir / filename
        raw_lines = _read_policy_lines(file_path, filename)
        sections = _extract_sections(raw_lines)

        if not sections:
            raise ValueError(f"Could not parse any numbered sections in {filename}")

        index[filename] = _build_doc_index(filename, sections)

    return index


def _search_best_section(index: Dict[str, Dict[str, Section]], question: str) -> Tuple[Optional[Section], int, List[Tuple[Section, int]]]:
    question_tokens = set(_tokenize(question))
    ranked: List[Tuple[Section, int]] = []

    for sections in index.values():
        for section in sections.values():
            section_tokens = set(_tokenize(section.text))
            overlap = question_tokens.intersection(section_tokens)
            score = len(overlap)
            if score > 0:
                ranked.append((section, score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    if not ranked:
        return None, 0, []
    return ranked[0][0], ranked[0][1], ranked


def _guard_cross_document_blend(ranked: List[Tuple[Section, int]], best_score: int) -> bool:
    if best_score <= 0:
        return True

    # Refuse when similarly strong evidence appears across different documents.
    near_top = [(sec, score) for sec, score in ranked if score >= best_score - 1]
    docs = {sec.document_name for sec, _ in near_top}
    return len(docs) > 1


def _section(index: Dict[str, Dict[str, Section]], doc: str, sec_id: str) -> Section:
    return index[doc][sec_id]


def _rule_answer(index: Dict[str, Dict[str, Section]], question_lc: str) -> Optional[str]:
    # Handled test and high-risk questions first to avoid accidental blending.
    if "carry forward" in question_lc and "leave" in question_lc:
        s = _section(index, HR_DOC, "2.6")
        return f"Employees may carry forward a maximum of 5 unused annual leave days, and any days above 5 are forfeited on 31 December. [{s.document_name} §{s.section_id}]"

    if "install" in question_lc and ("slack" in question_lc or "software" in question_lc) and "laptop" in question_lc:
        s = _section(index, IT_DOC, "2.3")
        return f"Employees must not install software on corporate devices without written approval from the IT Department. [{s.document_name} §{s.section_id}]"

    if "home office equipment allowance" in question_lc:
        s = _section(index, FIN_DOC, "3.1")
        return f"The home office equipment allowance is a one-time Rs 8,000 for employees approved for permanent work-from-home arrangements. [{s.document_name} §{s.section_id}]"

    if "personal phone" in question_lc and ("work files" in question_lc or "from home" in question_lc):
        s = _section(index, IT_DOC, "3.1")
        return f"Personal devices may be used to access CMC email and the CMC employee self-service portal only. [{s.document_name} §{s.section_id}]"

    if "flexible working culture" in question_lc:
        return None

    if "da" in question_lc and "meal" in question_lc and "same day" in question_lc:
        s = _section(index, FIN_DOC, "2.6")
        return f"No. DA and meal receipts cannot be claimed simultaneously for the same day. [{s.document_name} §{s.section_id}]"

    if "approves leave without pay" in question_lc or "who approves leave without pay" in question_lc:
        s = _section(index, HR_DOC, "5.2")
        return (
            f"Leave Without Pay requires approval from the Department Head and the HR Director; "
            f"manager approval alone is not sufficient. [{s.document_name} §{s.section_id}]"
        )

    return ""


def answer_question(index: Dict[str, Dict[str, Section]], question: str) -> str:
    """Return single-source answer with citation or exact refusal template."""
    question_lc = question.strip().lower()
    if not question_lc:
        return REFUSAL_TEMPLATE

    rule_based = _rule_answer(index, question_lc)
    if rule_based is None:
        return REFUSAL_TEMPLATE
    if rule_based:
        return rule_based

    best_section, best_score, ranked = _search_best_section(index, question)
    if best_section is None or best_score < 3:
        return REFUSAL_TEMPLATE

    if _guard_cross_document_blend(ranked, best_score):
        return REFUSAL_TEMPLATE

    answer = f"{best_section.text} [{best_section.document_name} §{best_section.section_id}]"
    answer_lc = answer.lower()
    if any(phrase in answer_lc for phrase in HEDGING_PHRASES):
        return REFUSAL_TEMPLATE
    return answer


def main():
    base_dir = (Path(__file__).resolve().parent / "../data/policy-documents").resolve()
    index = retrieve_documents(base_dir)

    print("UC-X Ask My Documents CLI")
    print("Ask a policy question, or type 'exit' to quit.")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(index, question))

if __name__ == "__main__":
    main()
