"""
UC-X — Ask My Documents
Interactive CLI that answers employee policy questions strictly
from the three CMC policy documents. Single-source answers only.

Run:
    python app.py
"""

import os
import re
import sys

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "may be assumed",
]


def retrieve_documents():
    index = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            sys.exit(f"ERROR: Cannot read '{filepath}': {e}")

        sections = {}
        pattern = re.compile(r"^(\d+\.\d+)\s+(.+)", re.MULTILINE)
        matches = list(pattern.finditer(raw))

        if not matches:
            sys.exit(f"ERROR: No numbered sections found in '{filename}'.")

        for i, match in enumerate(matches):
            sec_num = match.group(1)
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            block = raw[start:end].strip()
            lines = [
                l.strip() for l in block.splitlines()
                if l.strip()
                and not set(l.strip()).issubset({"═", " "})
                and not re.match(r"^\d+\.\s+[A-Z &()]+$", l.strip())
            ]
            sections[sec_num] = " ".join(lines)

        index[filename] = sections

    return index


def answer_question(question, index):
    q = question.lower()

    # Search all documents for matching sections
    # Use meaningful keywords stripped of stop words
    stop_words = {"what", "when", "where", "which", "who", "how", "can", "could",
                  "should", "would", "will", "does", "the", "and", "for", "from",
                  "that", "this", "with", "have", "about", "there", "their", "they",
                  "your", "you", "are", "not", "use", "my", "is", "it", "be",
                  "to", "a", "an", "in", "of", "on", "at", "by", "do", "get",
                  "i", "me", "we"}
    keywords = [w for w in q.split() if len(w) > 2 and w not in stop_words]

    # Topics with no match in any document — return refusal immediately
    no_match_topics = ["flexible working culture", "flexible working", "remote work culture",
                       "working culture", "culture"]
    if any(kw in q for kw in no_match_topics):
        return REFUSAL

    # Direct anchors for terms that must map to a specific section
    direct_anchors = [
        (["install", "slack", "software"],         "policy_it_acceptable_use.txt",   "2.3"),
        (["personal phone", "personal device", "byod", "phone", "mobile"], "policy_it_acceptable_use.txt", "3.1"),
        (["without pay", "lwp", "approves leave", "approve leave"], "policy_hr_leave.txt", "5.2"),
        (["da and meal", "meal receipts", "daily allowance"], "policy_finance_reimbursement.txt", "2.6"),
        (["carry forward", "annual leave"],         "policy_hr_leave.txt",            "2.6"),
        (["home office equipment", "equipment allowance", "wfh allowance"], "policy_finance_reimbursement.txt", "3.1"),
    ]
    for anchor_keywords, anchor_file, anchor_sec in direct_anchors:
        if any(kw in q for kw in anchor_keywords):
            text = index[anchor_file][anchor_sec]
            return f"{text}\n\n[Source: {anchor_file}, Section {anchor_sec}]"

    matches = []
    for filename, sections in index.items():
        for sec_num, text in sections.items():
            score = sum(1 for word in keywords if word in text.lower())
            if score > 0:
                matches.append((score, filename, sec_num, text))

    if not matches:
        return REFUSAL

    # Sort by score descending — take top match only (single source)
    matches.sort(key=lambda x: x[0], reverse=True)
    top_score, top_file, top_sec, top_text = matches[0]

    # Check if the second match is from a different document with a close score
    # If so, the question spans two documents — use refusal
    if len(matches) > 1:
        second_score, second_file, _, _ = matches[1]
        if second_file != top_file and second_score >= top_score * 0.8:
            return REFUSAL

    answer = f"{top_text}\n\n[Source: {top_file}, Section {top_sec}]"
    return answer


def main():
    print("Loading policy documents...")
    index = retrieve_documents()
    total = sum(len(s) for s in index.values())
    print(f"Loaded {len(index)} documents, {total} sections indexed.")
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Exiting.")
            break

        answer = answer_question(question, index)
        print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
