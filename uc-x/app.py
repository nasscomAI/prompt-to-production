"""
UC-X app.py — NAIVE BASELINE (Control step).
Mirrors what "Answer questions about company policy." naively produces:
a loose full-text keyword search across ALL documents combined, blending
whichever sentences look relevant regardless of which file they came from,
with hedging language when confidence is low. Kept here temporarily to
document the Control run; see git history.
"""
import glob
import re

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def load_all_text():
    blob = ""
    for path in DOC_PATHS:
        with open(path, encoding="utf-8") as f:
            blob += f.read() + "\n"
    return blob


def naive_answer(question: str, blob: str) -> str:
    words = [w.lower() for w in re.findall(r"[a-zA-Z]+", question) if len(w) > 3]
    sentences = re.split(r"(?<=[.\n])\s+", blob)
    hits = [s.strip() for s in sentences if any(w in s.lower() for w in words)]
    if not hits:
        return "While not explicitly covered, it is generally understood that standard policy applies here."
    # Blend whatever sentences matched, regardless of source document.
    return "Based on the documents: " + " ".join(hits[:3])


def main():
    blob = load_all_text()
    print("UC-X naive Q&A (Control step). Type a question, or 'exit' to quit.")
    while True:
        try:
            question = input("> ")
        except EOFError:
            break
        if question.strip().lower() in ("exit", "quit"):
            break
        print(naive_answer(question, blob))


if __name__ == "__main__":
    main()
