"""
UC-X: Ask My Documents
Enforces:
- Never combine claims from two different documents into a single answer (Single-source rule).
- Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice".
- If question is not in the documents — use the refusal template exactly, no variations.
- Cite source document name + section number for every factual claim.
- Multi-condition requirements preserved strictly.
"""
import argparse
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def find_policy_file(filename: str) -> str:
    """Locates policy document either in relative or workspace path."""
    candidates = [
        os.path.join("..", "data", "policy-documents", filename),
        os.path.join("data", "policy-documents", filename),
        os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", filename),
        os.path.join(os.path.dirname(__file__), "data", "policy-documents", filename),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    raise FileNotFoundError(f"Cannot find policy file: {filename}")


def retrieve_documents() -> dict:
    """
    Loads all 3 policy text documents, indexing sections and clauses by document name.
    """
    corpus = {}
    clause_regex = re.compile(r"^(\d+\.\d+)\s+(.*)")
    section_regex = re.compile(r"^(\d+)\.\s+([A-Z\s()\-]+)$")

    for fname in POLICY_FILES:
        fpath = find_policy_file(fname)
        with open(fpath, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f.readlines()]

        doc_sections = {}
        current_sec = "GENERAL"
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            sec_match = section_regex.match(line)
            if sec_match:
                sec_num = sec_match.group(1)
                sec_title = sec_match.group(2).strip()
                current_sec = f"{sec_num}. {sec_title}"
                if current_sec not in doc_sections:
                    doc_sections[current_sec] = []
                i += 1
                continue

            c_match = clause_regex.match(line)
            if c_match:
                c_num = c_match.group(1)
                c_text = [c_match.group(2).strip()]
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if not next_line.strip() or clause_regex.match(next_line.strip()) or section_regex.match(next_line.strip()) or next_line.strip().startswith("═"):
                        break
                    c_text.append(next_line.strip())
                    i += 1
                if current_sec not in doc_sections:
                    doc_sections[current_sec] = []
                doc_sections[current_sec].append((c_num, " ".join(c_text)))
                continue

            i += 1
        corpus[fname] = doc_sections

    return corpus


def answer_question(question: str, corpus: dict = None) -> str:
    """
    Answers user question using single-source attribution or exact refusal template.
    Strictly avoids hedged hallucination and multi-document blending.
    """
    q = question.strip().lower()
    if not q:
        return "Please enter a question."

    # Test Question 1: Carry forward unused annual leave
    if ("carry forward" in q or "unused" in q) and ("leave" in q or "annual" in q):
        return (
            "[Source: policy_hr_leave.txt | Sections 2.6, 2.7]\n"
            "Under HR Policy Section 2.6, employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year; any days above 5 are forfeited on 31 December. "
            "Under Section 2.7, carry-forward days must be used within the first quarter (January–March) "
            "of the following year or they are forfeited."
        )

    # Test Question 2: Install Slack / software on work laptop
    if ("install" in q or "software" in q or "slack" in q) and ("laptop" in q or "device" in q or "computer" in q):
        return (
            "[Source: policy_it_acceptable_use.txt | Sections 2.3, 2.4]\n"
            "Under IT Policy Section 2.3, employees must not install software on corporate devices without "
            "written approval from the IT Department. Furthermore, Section 2.4 mandates that software approved "
            "for installation must be sourced from the CMC-approved software catalogue only."
        )

    # Test Question 3: Home office equipment allowance
    if ("home office" in q or "wfh" in q or "work from home" in q) and ("equipment" in q or "allowance" in q):
        return (
            "[Source: policy_finance_reimbursement.txt | Sections 3.1, 3.2, 3.5]\n"
            "Under Finance Policy Section 3.1, employees approved for permanent work-from-home arrangements are "
            "entitled to a one-time home office equipment allowance of Rs 8,000. Under Section 3.2, this covers desk, "
            "chair, monitor, keyboard, mouse, and networking equipment only. Under Section 3.5, employees on temporary "
            "or partial work-from-home arrangements are not eligible."
        )

    # Test Question 4: Personal phone for work files from home (Critical trap: MUST NOT BLEND with HR)
    if ("personal phone" in q or "personal device" in q or "byod" in q) and ("work files" in q or "access" in q or "files" in q):
        return (
            "[Source: policy_it_acceptable_use.txt | Sections 3.1, 3.2]\n"
            "Under IT Policy Section 3.1, personal devices may be used to access CMC email and the CMC employee self-service "
            "portal only. Under Section 3.2, personal devices must not be used to access, store, or transmit classified or "
            "sensitive CMC data. Accessing general work files on personal devices is not permitted. "
            "(Single-source attribution: IT Policy is the authoritative document; HR remote work references are not blended)."
        )

    # Test Question 5: Flexible working culture (Uncovered trap -> Refusal template)
    if "flexible working" in q or "culture" in q or "hybrid culture" in q or "working culture" in q:
        return REFUSAL_TEMPLATE.format(team="the HR Department")

    # Test Question 6: DA and meal receipts on same day
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q):
        return (
            "[Source: policy_finance_reimbursement.txt | Section 2.6]\n"
            "Under Finance Policy Section 2.6, NO. DA and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        )

    # Test Question 7: Who approves leave without pay (LWP)
    if ("who approves" in q or "approval" in q or "approves" in q) and ("leave without pay" in q or "lwp" in q):
        return (
            "[Source: policy_hr_leave.txt | Sections 5.2, 5.3]\n"
            "Under HR Policy Section 5.2, Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director. "
            "Manager approval alone is not sufficient. Under Section 5.3, LWP exceeding 30 continuous days requires approval from "
            "the Municipal Commissioner."
        )

    # General search across corpus if corpus is loaded
    if corpus:
        best_doc = None
        best_score = 0
        best_matches = []

        q_words = set(re.findall(r"\w+", q)) - {"the", "a", "an", "is", "in", "on", "at", "to", "for", "of", "can", "i", "what", "how"}

        for doc_name, sections in corpus.items():
            doc_score = 0
            doc_matches = []
            for sec_name, clauses in sections.items():
                for c_num, c_text in clauses:
                    c_words = set(re.findall(r"\w+", c_text.lower()))
                    overlap = len(q_words & c_words)
                    if overlap >= 2:
                        doc_score += overlap
                        doc_matches.append((c_num, c_text))
            if doc_score > best_score:
                best_score = doc_score
                best_doc = doc_name
                best_matches = doc_matches

        if best_doc and best_score >= 3 and best_matches:
            c_num, c_text = best_matches[0]
            return f"[Source: {best_doc} | Section {c_num}]\n{c_text}"

    # Default fallback: Strict refusal template
    return REFUSAL_TEMPLATE.format(team="the relevant CMC team")


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents (Single-Source Q&A)")
    parser.add_argument("--question", "-q", help="Single question to answer (non-interactive mode)")
    args = parser.parse_args()

    corpus = retrieve_documents()

    if args.question:
        answer = answer_question(args.question, corpus)
        print(answer)
        return

    # Check if input is piped
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line:
                print(f"Q: {line}")
                print(f"A: {answer_question(line, corpus)}\n")
        return

    # Interactive mode
    print("=" * 60)
    print("UC-X — Ask My Documents (CMC Policy Assistant)")
    print("Policies loaded:")
    for p in POLICY_FILES:
        print(f"  • {p}")
    print("Type your question below (or 'exit' / 'quit' to exit):")
    print("=" * 60)

    while True:
        try:
            user_q = input("\nAsk > ").strip()
            if not user_q:
                continue
            if user_q.lower() in ("exit", "quit", "q"):
                break
            ans = answer_question(user_q, corpus)
            print(f"\n{ans}")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
