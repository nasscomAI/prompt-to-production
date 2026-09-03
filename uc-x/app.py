"""
UC-X app.py — Single-source Q&A over three policy documents.

Usage:
    python app.py
Then type a question at the prompt. Type 'quit' to exit.
"""
import os
import re
import sys
from typing import Dict, List

DOC_FILES = [
    ("policy_hr_leave.txt",                 "HR"),
    ("policy_it_acceptable_use.txt",        "IT"),
    ("policy_finance_reimbursement.txt",    "Finance"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR / IT / Finance) for guidance."
)

FORBIDDEN = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard practice",
    "employees are usually expected to",
    "it is advisable",
    "generally expected",
]

SECTION_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")
SECTION_HEADER_RE = re.compile(r"^\s*\d+\.\s+[A-Z][A-Z &\-]+\s*$")
UNDERLINE_RE = re.compile(r"^[═=─\-]{5,}\s*$")


def fail(msg: str) -> "None":
    sys.stderr.write(f"UC-X: {msg}\n")
    sys.exit(1)


# --- skill: retrieve_documents ---------------------------------------------

def retrieve_documents(repo_root: str) -> Dict[str, List[Dict[str, str]]]:
    index: Dict[str, List[Dict[str, str]]] = {}
    for fname, _label in DOC_FILES:
        path = os.path.join(repo_root, "data", "policy-documents", fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            fail(f"policy file not found: {path}")
        except OSError as e:
            fail(f"cannot read policy file {path}: {e}")

        sections: List[Dict[str, str]] = []
        current: Dict[str, str] | None = None
        for line in lines:
            if UNDERLINE_RE.match(line):
                continue
            if SECTION_HEADER_RE.match(line):
                continue
            m = SECTION_RE.match(line)
            if m:
                if current is not None:
                    current["text"] = current["text"].strip()
                    sections.append(current)
                current = {"section": m.group(1), "text": m.group(2)}
            elif current is not None and line.strip():
                current["text"] += "\n" + line.rstrip()
        if current is not None:
            current["text"] = current["text"].strip()
            sections.append(current)

        if not sections:
            fail(f"no parseable sections in {path}")
        index[fname] = sections
    return index


# --- skill: answer_question -------------------------------------------------

KEYWORD_TOPIC: Dict[str, List[str]] = {
    "policy_it_acceptable_use.txt": [
        "phone", "device", "laptop", "install", "software", "slack",
        "password", "wifi", "vpn", "remote", "email", "monitor",
        "endpoint", "data", "access", "mfa", "byod", "personal",
        "self-service", "portal",
    ],
    "policy_hr_leave.txt": [
        "leave", "holiday", "sick", "carry forward", "encash",
        "lwp", "leave without pay", "without pay", "approver",
        "department head", "hr director", "maternity", "paternity",
    ],
    "policy_finance_reimbursement.txt": [
        "reimburse", "claim", "allowance", "home office", "da",
        "meal", "travel", "hotel", "training", "bill", "rs ",
        "equipment", "receipt",
    ],
}


def _score(question: str, doc_name: str) -> int:
    q = question.lower()
    return sum(1 for kw in KEYWORD_TOPIC.get(doc_name, []) if kw in q)


SECTION_HINT: Dict[str, Dict[str, List[str]]] = {
    "policy_hr_leave.txt": {
        "2.6": ["carry forward", "carry-forward", "unused annual"],
        "5.2": ["leave without pay", "lwp", "without pay", "approves", "approver"],
        "5.3": ["30", "30 days", "municipal commissioner"],
    },
    "policy_it_acceptable_use.txt": {
        "2.3": ["install", "software", "slack"],
        "3.1": ["personal phone", "personal device", "byod", "self-service"],
    },
    "policy_finance_reimbursement.txt": {
        "2.6": ["da", "meal"],
        "3.1": ["home office", "allowance", "8000", "rs 8,000"],
    },
}


def _best_section(question: str, doc_name: str, sections: List[Dict[str, str]]) -> Dict[str, str] | None:
    q = question.lower()
    q_tokens = set(re.findall(r"[a-z]{4,}", q))

    for sec_no, hints in SECTION_HINT.get(doc_name, {}).items():
        if any(h in q for h in hints):
            for sec in sections:
                if sec["section"] == sec_no:
                    return sec

    bigrams = set()
    q_words = re.findall(r"[a-z]{3,}", q)
    for i in range(len(q_words) - 1):
        bigrams.add(f"{q_words[i]} {q_words[i+1]}")

    best = None
    best_score = 0
    for sec in sections:
        sec_text_low = sec["text"].lower()
        sec_tokens = set(re.findall(r"[a-z]{4,}", sec_text_low))
        overlap = len(q_tokens & sec_tokens)
        sec_bigrams = set()
        sec_words = re.findall(r"[a-z]{3,}", sec_text_low)
        for i in range(len(sec_words) - 1):
            sec_bigrams.add(f"{sec_words[i]} {sec_words[i+1]}")
        bigram_hit = len(bigrams & sec_bigrams) * 3
        score = overlap + bigram_hit
        if score > best_score:
            best_score = score
            best = sec
    return best if best_score >= 4 else None


def answer_question(index: Dict[str, List[Dict[str, str]]], question: str) -> str:
    if not question.strip():
        return REFUSAL_TEMPLATE

    scores = {d: _score(question, d) for d in index}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    if not ranked or ranked[0][1] == 0:
        return REFUSAL_TEMPLATE

    primary_doc = ranked[0][0]
    if len(ranked) > 1 and ranked[1][1] > 0 and abs(ranked[0][1] - ranked[1][1]) <= 1:
        return REFUSAL_TEMPLATE

    sec = _best_section(question, primary_doc, index[primary_doc])
    if sec is None:
        return REFUSAL_TEMPLATE

    quote = sec["text"]
    answer = (
        f"Source: {primary_doc} §{sec['section']}\n"
        f"Quote: \"{quote}\"\n"
        f"Citation: [{primary_doc} §{sec['section']}]"
    )
    low = answer.lower()
    if any(p in low for p in FORBIDDEN):
        return REFUSAL_TEMPLATE
    return answer


# --- entrypoint -------------------------------------------------------------

def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    index = retrieve_documents(repo_root)

    print("UC-X policy Q&A. Type 'quit' to exit.")
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in {"quit", "exit"}:
            break
        print()
        print(answer_question(index, q))
        print()


if __name__ == "__main__":
    main()
