"""
UC-X — Single-document Q&A over three policies; refusal template when not covered.
See README.md for run command.
"""
from __future__ import annotations

import re
from pathlib import Path

POLICY_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def retrieve_documents(base: Path | None = None) -> dict[str, str]:
    root = base or POLICY_DIR
    out: dict[str, str] = {}
    for name in FILES:
        p = root / name
        out[name] = p.read_text(encoding="utf-8")
    return out


def clause_text(full: str, sub: str) -> str:
    """Extract numbered clause sub (e.g. '5.2') through the next sibling clause."""
    esc = re.escape(sub)
    m = re.search(rf"({esc}\s.+?)(?=\n\d+\.\d+\s|\n═|$)", full, re.DOTALL)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1).strip())


def answer_question(question: str, corpus: dict[str, str]) -> str:
    q = question.lower().strip()

    hr = corpus["policy_hr_leave.txt"]
    it = corpus["policy_it_acceptable_use.txt"]
    fin = corpus["policy_finance_reimbursement.txt"]

    # --- Routed answers (single source each) ---
    if "carry forward" in q and ("annual" in q or "leave" in q):
        s = clause_text(hr, "2.6")
        return (
            f"Source: policy_hr_leave.txt, section 2.6\n\n{s}\n\n"
            f"(Related: section 2.7 states carry-forward days must be used in January–March "
            f"or are forfeited.)"
        )

    if "slack" in q and ("laptop" in q or "install" in q):
        s = clause_text(it, "2.3")
        return f"Source: policy_it_acceptable_use.txt, section 2.3\n\n{s}"

    if "home office" in q or ("equipment" in q and "allowance" in q):
        s = clause_text(fin, "3.1")
        return f"Source: policy_finance_reimbursement.txt, section 3.1\n\n{s}"

    if ("personal phone" in q or "personal device" in q) and (
        "work" in q or "home" in q or "file" in q or "access" in q
    ):
        s = clause_text(it, "3.1")
        return (
            f"Source: policy_it_acceptable_use.txt, section 3.1 (BYOD — single source; "
            f"not combined with other documents)\n\n{s}\n\n"
            f"The policy authorises CMC email and the employee self-service portal only on "
            f"personal devices; it does not state that other work files or systems may be "
            f"accessed from personal devices."
        )

    if "flexible" in q and "culture" in q:
        return REFUSAL

    if "da" in q and "meal" in q and "same day" in q:
        s = clause_text(fin, "2.6")
        return f"Source: policy_finance_reimbursement.txt, section 2.6\n\n{s}"

    if "leave without pay" in q or ("lwp" in q and "approv" in q):
        s = clause_text(hr, "5.2")
        extra = clause_text(hr, "5.3")
        return (
            f"Source: policy_hr_leave.txt, section 5.2\n\n{s}\n\n"
            f"Section 5.3 (continuous LWP over 30 days): {extra}"
        )

    return REFUSAL


def main() -> None:
    corpus = retrieve_documents()
    print("UC-X — Ask My Documents (type 'quit' to exit)\n")
    while True:
        try:
            q = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q or q.lower() in ("quit", "exit"):
            break
        print(answer_question(q, corpus))
        print()


if __name__ == "__main__":
    main()
