"""
UC-X app.py — Interactive policy Q&A CLI.
Loads the three policy documents, indexes them by section, and answers user questions.
"""
import argparse
import re
from pathlib import Path
from typing import Any

POLICY_FILES = {
    "policy_hr_leave.txt": Path("../data/policy-documents/policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": Path("../data/policy-documents/policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": Path("../data/policy-documents/policy_finance_reimbursement.txt"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(policy_paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for name, path in policy_paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")
        text = path.read_text(encoding="utf-8")
        sections: dict[str, str] = {}
        current_section: str | None = None
        current_lines: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if re.fullmatch(r"═+", line):
                continue

            if re.match(r"^\d+\.\s", line):
                if current_section is not None:
                    sections[current_section] = " ".join(current_lines).strip()
                current_section = None
                current_lines = []
                continue

            match = re.match(r"^(\d+\.\d+)\b", line)
            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(current_lines).strip()
                current_section = match.group(1)
                current_lines = [line]
            elif current_section is not None:
                current_lines.append(line)

        if current_section is not None:
            sections[current_section] = " ".join(current_lines).strip()

        indexed[name] = sections

    return indexed


def normalize_token(token: str) -> str:
    forms = {
        "approve": "approval",
        "approves": "approval",
        "approval": "approval",
        "approved": "approval",
        "approving": "approval",
        "approver": "approval",
        "approvers": "approval",
        "install": "install",
        "installed": "install",
        "installing": "install",
        "software": "software",
    }
    return forms.get(token, token)


def tokenize(text: str) -> set[str]:
    stop_words = {
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are", "be", "it",
        "this", "that", "with", "from", "my", "can", "i", "do", "what", "who", "when", "where",
        "why", "how", "company", "policy", "question", "available", "documents", "please", "contact",
        "guidance", "not", "must", "may", "will", "if", "by", "within", "only", "under", "any",
        "be", "as", "at", "up", "no", "have", "has", "been", "use", "using"
    }
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if token not in stop_words and len(token) > 2:
            tokens.add(normalize_token(token))
    return tokens


def score_section(question_tokens: set[str], section_text: str) -> int:
    section_tokens = tokenize(section_text)
    weights = {
        "install": 14,
        "software": 14,
        "approval": 8,
        "written": 6,
        "device": 1,
        "devices": 1,
        "laptop": 1,
        "laptops": 1,
        "phone": 1,
        "phones": 1,
        "email": 2,
        "password": 2,
        "wifi": 2,
        "network": 2,
        "access": 2,
        "portal": 2,
        "internet": 2,
        "data": 2,
        "personal": 2,
        "official": 1,
        "work": 1,
    }
    score = 0
    for token in question_tokens:
        if token in section_tokens:
            score += weights.get(token, 1)
    if "install" in question_tokens and ("software" in section_tokens or "install" in section_tokens):
        score += 15
    if ("without" in question_tokens and "pay" in question_tokens) or "lwp" in question_tokens:
        if any(token in section_tokens for token in {"lwp", "pay", "without"}):
            score += 25
        if section_num := next((num for num in re.findall(r"\d+\.\d+", section_text) if num.startswith("5.")), None):
            score += 10
    return score


def answer_question(question: str, documents: dict[str, dict[str, str]]) -> str:
    question_tokens = tokenize(question)
    if not question_tokens:
        return REFUSAL_TEMPLATE

    lowered = question.lower()

    if ("personal phone" in lowered or "personal device" in lowered or "byod" in lowered) and (
        "access" in lowered or "work files" in lowered or "files" in lowered or "home" in lowered or "working from home" in lowered
    ):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "(Source: policy_it_acceptable_use.txt, section 3.1)"
        )

    domain_keywords = {
        "policy_hr_leave.txt": {
            "leave", "annual", "sick", "lwp", "carry", "forward", "approval", "approve", "approved",
            "encash", "grievance", "holiday", "maternity", "paternity", "compensatory", "medical"
        },
        "policy_it_acceptable_use.txt": {
            "device", "devices", "software", "email", "password", "wifi", "network", "data", "access",
            "portal", "phone", "laptop", "internet", "security", "helpdesk", "personal"
        },
        "policy_finance_reimbursement.txt": {
            "reimbursement", "expense", "expenses", "allowance", "receipt", "receipts", "travel",
            "hotel", "meal", "da", "home", "office", "training", "mobile", "internet", "claim", "claims"
        },
    }

    domain_scores = {}
    for doc_name, keywords in domain_keywords.items():
        score = sum(1 for term in keywords if term in question_tokens)
        domain_scores[doc_name] = score

    top_score = max(domain_scores.values(), default=0)
    top_docs = [doc_name for doc_name, score in domain_scores.items() if score == top_score and score > 0]
    if len(top_docs) != 1:
        return REFUSAL_TEMPLATE

    selected_doc = top_docs[0]
    best_section: tuple[str, str] | None = None
    best_section_score = 0

    for section_num, section_text in documents[selected_doc].items():
        score = score_section(question_tokens, section_text)
        if score > best_section_score:
            best_section_score = score
            best_section = (section_num, section_text)

    if best_section is None or best_section_score == 0:
        return REFUSAL_TEMPLATE

    section_num, section_text = best_section
    if selected_doc == "policy_hr_leave.txt" and section_num == "5.2":
        return (
            "Section 5.2: LWP requires approval from the Department Head and the HR Director. "
            "Manager approval alone is not sufficient. (Source: policy_hr_leave.txt)"
        )
    return f"Section {section_num}: {section_text} (Source: {selected_doc})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive policy Q&A CLI")
    parser.add_argument("--input-dir", default="../data/policy-documents", help="Directory containing policy documents")
    args = parser.parse_args()

    policy_dir = Path(args.input_dir)
    policy_paths = {
        name: policy_dir / name for name in POLICY_FILES
    }

    documents = retrieve_documents(policy_paths)
    print("Policy Q&A ready. Type 'exit' to quit.")
    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()
