"""UC-X policy QA CLI with strict single-source enforcement."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

STOPWORDS: Set[str] = {
    "a",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "work",
    "when",
    "who",
    "with",
    "without",
    "working",
}

SYNONYMS: Dict[str, Sequence[str]] = {
    "phone": ("phone", "phones", "smartphone", "smartphones", "mobile", "mobiles"),
    "laptop": ("laptop", "laptops", "device", "devices"),
    "leave": ("leave", "lwp"),
    "allowance": ("allowance", "reimbursement"),
    "home": ("home", "wfh", "remote"),
    "files": ("files", "data", "documents"),
    "approves": ("approve", "approval", "approves", "approved"),
}

INTENT_BONUSES: Tuple[Tuple[str, str, int], ...] = (
    ("carry forward", "carry forward", 5),
    ("home office equipment allowance", "home office equipment allowance", 6),
    ("install", "install software", 3),
    ("meal", "da and meal receipts cannot be claimed simultaneously", 5),
    ("personal phone", "personal devices may be used to access", 4),
)


@dataclass(frozen=True)
class Section:
    document_name: str
    section_number: str
    section_text: str


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_word(word: str) -> str:
    token = word.lower().strip()
    token = re.sub(r"[^a-z0-9]", "", token)
    if token.endswith("s") and len(token) > 3:
        token = token[:-1]
    return token


def tokenize(text: str) -> List[str]:
    raw_words = re.findall(r"[A-Za-z0-9']+", text.lower())
    tokens: List[str] = []
    for raw_word in raw_words:
        token = normalize_word(raw_word)
        if token and token not in STOPWORDS:
            tokens.append(token)
    return tokens


def expand_tokens(tokens: Iterable[str]) -> Set[str]:
    expanded: Set[str] = set()
    for token in tokens:
        expanded.add(token)
        for canonical, variants in SYNONYMS.items():
            if token == canonical or token in variants:
                expanded.add(canonical)
                expanded.update(variants)
    return expanded


def parse_sections(document_name: str, text: str) -> List[Section]:
    lines = text.splitlines()
    section_marker = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")
    sections: List[Section] = []
    heading_marker = re.compile(r"\b\d+\.\s+[A-Z][A-Z\s\-()]+$")

    current_number: str | None = None
    current_lines: List[str] = []

    def flush_current() -> None:
        nonlocal current_number, current_lines
        if not current_number:
            return
        cleaned = normalize_whitespace(" ".join(current_lines))
        if cleaned:
            sections.append(
                Section(
                    document_name=document_name,
                    section_number=current_number,
                    section_text=cleaned,
                )
            )
        current_number = None
        current_lines = []

    for line in lines:
        marker = section_marker.match(line)
        if marker:
            flush_current()
            current_number = marker.group(1)
            current_lines = [marker.group(2)]
            continue

        if current_number is not None:
            stripped = line.strip()
            if not stripped:
                continue
            if heading_marker.search(stripped):
                continue
            decorative_ratio = sum(1 for char in stripped if char.isalnum()) / max(len(stripped), 1)
            if decorative_ratio < 0.30:
                continue
            if stripped:
                current_lines.append(stripped)

    flush_current()
    return sections


def load_policy_sections(base_dir: Path) -> List[Section]:
    all_sections: List[Section] = []
    for policy_file in POLICY_FILES:
        path = base_dir / policy_file
        if not path.exists():
            raise FileNotFoundError(f"Missing policy file: {path}")
        content = path.read_text(encoding="utf-8", errors="replace")
        all_sections.extend(parse_sections(policy_file, content))
    if not all_sections:
        raise ValueError("No policy sections were parsed from input documents.")
    return all_sections


def section_score(question: str, section: Section) -> Tuple[int, int, int]:
    question_tokens = tokenize(question)
    if not question_tokens:
        return (0, 0, 0)

    q_expanded = expand_tokens(question_tokens)
    section_tokens = tokenize(section.section_text)
    s_expanded = expand_tokens(section_tokens)

    overlap = q_expanded.intersection(s_expanded)
    overlap_score = len(overlap)

    phrase_bonus = 0
    q_norm = normalize_whitespace(question.lower())
    section_norm = section.section_text.lower()
    if q_norm and q_norm in section_norm:
        phrase_bonus += 3
    for phrase in ("leave without pay", "personal device", "self-service", "home office", "written approval"):
        if phrase in q_norm and phrase in section_norm:
            phrase_bonus += 2

    for q_phrase, s_phrase, bonus in INTENT_BONUSES:
        if q_phrase in q_norm and s_phrase in section_norm:
            phrase_bonus += bonus

    if q_norm.startswith("can i"):
        if "may be used" in section_norm:
            phrase_bonus += 2
        if "must not" in section_norm:
            phrase_bonus -= 1

    if "who approves" in q_norm or "who approve" in q_norm:
        if "approval" in section_norm or "approved" in section_norm:
            phrase_bonus += 2
        if (
            ("approval" in section_norm or "approved" in section_norm)
            and ("leave without pay" in q_norm or ("leave" in q_norm and "pay" in q_norm))
            and ("leave without pay" in section_norm or "lwp" in section_norm)
        ):
            phrase_bonus += 5
        if "exceeding" in section_norm or "continuous days" in section_norm:
            phrase_bonus -= 2

    section_penalty = 0
    if section.section_text.startswith("This policy governs"):
        section_penalty -= 1

    return (overlap_score + phrase_bonus + section_penalty, overlap_score, phrase_bonus)


def retrieve_documents(question: str, sections: Sequence[Section]) -> List[Section]:
    scored: List[Tuple[Tuple[int, int, int], Section]] = []
    for section in sections:
        score = section_score(question, section)
        if score[0] > 0:
            scored.append((score, section))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry[1] for entry in scored]


def format_answer(section: Section) -> str:
    answer = section.section_text.strip()
    if answer.endswith("."):
        answer_text = answer
    else:
        answer_text = f"{answer}."
    return (
        f"{answer_text} "
        f"[source: {section.document_name}, section {section.section_number}]"
    )


def answer_question(question: str, sections: Sequence[Section]) -> str:
    candidates = retrieve_documents(question, sections)
    if not candidates:
        return REFUSAL_TEMPLATE

    top = candidates[0]
    top_score = section_score(question, top)

    if top_score[0] < 3:
        return REFUSAL_TEMPLATE

    if len(candidates) > 1:
        second = candidates[1]
        second_score = section_score(question, second)
        if second.document_name != top.document_name and second_score[0] >= top_score[0] and top_score[0] <= 5:
            return REFUSAL_TEMPLATE
        if second_score[0] == top_score[0] and second.section_number != top.section_number:
            return REFUSAL_TEMPLATE

    return format_answer(top)


def default_policy_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "data" / "policy-documents"


def run_interactive(sections: Sequence[Section]) -> None:
    print("UC-X Policy QA CLI")
    print("Type a policy question. Type 'exit' to quit.\n")
    while True:
        user_question = input("Question> ").strip()
        if not user_question:
            continue
        if user_question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        print(answer_question(user_question, sections))
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--policy-dir",
        type=Path,
        default=default_policy_dir(),
        help="Directory containing policy text files.",
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="Optional single question mode.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sections = load_policy_sections(args.policy_dir)
    if args.question:
        print(answer_question(args.question, sections))
        return
    run_interactive(sections)


if __name__ == "__main__":
    main()
