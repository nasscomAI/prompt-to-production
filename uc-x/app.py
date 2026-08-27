"""
UC-X — Municipal Policy Question Answering Agent
Answers employee questions using only the three available policy documents.
Answers always cite a single source document and section number.
"""
import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

# Minimum keyword-match score to accept an answer (tuned conservatively
# so vague or off-topic questions trigger the refusal template)
MIN_SCORE = 2

# ---------------------------------------------------------------------------
# Intent rules — checked before generic scoring (first match wins).
# Each entry: (list_of_trigger_phrases, doc_name, section_number)
# ---------------------------------------------------------------------------
INTENT_RULES: list[tuple[list[str], str, str]] = [
    # IT policy — software installation (2.3)
    (
        ["install slack", "install software", "install app", "install program",
         "install application", "install anything", "slack on", "software on"],
        "policy_it_acceptable_use.txt", "2.3",
    ),
    # IT policy — personal / BYOD devices (3.1)
    (
        ["personal phone", "personal device", "personal mobile", "byod",
         "own phone", "own device", "own laptop", "personal laptop",
         "my phone", "my device"],
        "policy_it_acceptable_use.txt", "3.1",
    ),
    # HR leave — carry-forward annual leave (2.6)
    (
        ["carry forward", "carry-forward", "unused leave", "unused annual leave",
         "roll over leave", "rollover leave"],
        "policy_hr_leave.txt", "2.6",
    ),
    # HR leave — leave without pay approval (5.2)
    (
        ["leave without pay", "lwp approval", "lwp requires", "unpaid leave approval"],
        "policy_hr_leave.txt", "5.2",
    ),
    # Finance — home office / WFH equipment allowance (3.1)
    (
        ["home office equipment", "wfh allowance", "work from home allowance",
         "work-from-home allowance", "home office allowance", "wfh equipment"],
        "policy_finance_reimbursement.txt", "3.1",
    ),
    # Finance — DA and meal receipts (2.6)
    (
        ["da and meal", "claim da and meal", "daily allowance and meal",
         "meal receipts and da", "da with meal", "da or meal"],
        "policy_finance_reimbursement.txt", "2.6",
    ),
]

# Common stop words to ignore when scoring
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "up", "about", "into", "through",
    "i", "my", "me", "we", "our", "you", "your", "they", "their", "it",
    "its", "what", "how", "when", "where", "who", "which", "that", "this",
    "or", "and", "not", "if", "so", "but", "no", "any", "all", "as",
}


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(policy_dir: str, doc_names: list[str]) -> dict[str, dict[str, str]]:
    """
    Load and parse policy documents.
    Returns: {doc_name: {section_num: clause_text}}
    Terminates on file or parse error.
    """
    index: dict[str, dict[str, str]] = {}
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for doc_name in doc_names:
        path = os.path.join(policy_dir, doc_name)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as exc:
            sys.exit(f"Error: cannot load '{doc_name}': {exc}")

        clauses: dict[str, str] = {}
        current_key: str | None = None
        current_parts: list[str] = []

        for line in lines:
            m = clause_re.match(line)
            if m:
                if current_key:
                    clauses[current_key] = " ".join(current_parts).strip()
                current_key = m.group(1)
                current_parts = [m.group(2).strip()]
            elif current_key and line.startswith((" ", "\t")) and line.strip():
                current_parts.append(line.strip())
            elif line.strip() and not line.startswith((" ", "\t")):
                if current_key:
                    clauses[current_key] = " ".join(current_parts).strip()
                    current_key = None
                    current_parts = []

        if current_key:
            clauses[current_key] = " ".join(current_parts).strip()

        if not clauses:
            sys.exit(f"Error: no numbered clauses found in '{doc_name}'.")

        index[doc_name] = clauses

    return index


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    """Lowercase words, strip punctuation, remove stop words."""
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}


def answer_question(question: str, index: dict[str, dict[str, str]]) -> str:
    """
    Search indexed documents for clauses relevant to the question.
    Intent rules are checked first (exact phrase match, case-insensitive).
    Falls back to keyword-overlap scoring for unmatched questions.
    Returns a single-source cited answer or the refusal template.
    Never combines content from multiple documents.
    """
    q_lower = question.lower()

    # --- Pass 1: intent rules (first match wins) ---
    for triggers, doc_name, section_num in INTENT_RULES:
        if any(trigger in q_lower for trigger in triggers):
            clause_text = index.get(doc_name, {}).get(section_num)
            if clause_text:
                return (
                    f"Source: {doc_name}, Section {section_num}\n\n"
                    f"{clause_text}"
                )

    # --- Pass 2: generic keyword-overlap scoring ---
    q_tokens = _tokenize(question)
    if not q_tokens:
        return REFUSAL_TEMPLATE

    best_score = 0
    best_doc: str | None = None
    best_section: str | None = None
    best_text: str | None = None

    for doc_name, clauses in index.items():
        for section_num, clause_text in clauses.items():
            c_tokens = _tokenize(clause_text)
            score = len(q_tokens & c_tokens)
            if score > best_score:
                best_score = score
                best_doc = doc_name
                best_section = section_num
                best_text = clause_text

    if best_score < MIN_SCORE or best_doc is None:
        return REFUSAL_TEMPLATE

    return (
        f"Source: {best_doc}, Section {best_section}\n\n"
        f"{best_text}"
    )


# ---------------------------------------------------------------------------
# Entry point — interactive loop
# ---------------------------------------------------------------------------

def main():
    print("Municipal Policy Q&A")
    print("Documents loaded: " + ", ".join(DOCUMENTS))
    print('Type your question and press Enter. Type "exit" to quit.\n')

    index = retrieve_documents(POLICY_DIR, DOCUMENTS)

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() == "exit":
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
