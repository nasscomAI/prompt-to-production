"""
UC-X Ask My Documents — interactive CLI.

Implements `retrieve_documents` and `answer_question` skills and enforces
the refusal template defined in the UC-X README. Supports an interactive mode
and a single-question `--question` mode for scripting.
"""
from __future__ import annotations
import argparse
import os
import re
from typing import Dict, List, Tuple, Optional


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(file_paths: List[str]) -> Tuple[Dict[str, List[Dict]], List[str]]:
    """
    Load files and index by section/subsection. Returns (index, errors).
    index: filename -> list of {section: str, text: str}
    """
    index: Dict[str, List[Dict]] = {}
    errors: List[str] = []

    section_header_re = re.compile(r"^(\d+)\.\s+([A-Z0-9 \-&]+)")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for path in file_paths:
        if not os.path.exists(path):
            errors.append(f"Missing file: {path}")
            continue

        filename = os.path.basename(path)
        index[filename] = []

        with open(path, encoding="utf-8") as fh:
            lines = [l.rstrip("\n") for l in fh]

        current_section = None
        buffer: List[str] = []

        for line in lines:
            m_sec = section_header_re.match(line)
            m_clause = clause_re.match(line)
            if m_sec:
                # flush previous section
                if current_section is not None and buffer:
                    index[filename].append({"section": current_section, "text": "\n".join(buffer).strip()})
                current_section = m_sec.group(1)
                buffer = []
                continue
            if m_clause:
                # clause like 2.1 ... include as separate paragraph
                sect = m_clause.group(1)
                text = m_clause.group(2)
                index[filename].append({"section": sect, "text": text.strip()})
                continue

            # otherwise accumulate
            if line.strip() == "":
                continue
            buffer.append(line)

        if current_section is not None and buffer:
            index[filename].append({"section": current_section, "text": "\n".join(buffer).strip()})

    return index, errors


STOPWORDS = {"the", "is", "and", "or", "of", "a", "to", "in", "for", "on", "by", "with", "be", "not", "are", "this", "that", "it", "as", "from"}


def score_text(question: str, text: str) -> float:
    q_words = [w.lower() for w in re.findall(r"\w+", question) if w.lower() not in STOPWORDS]
    t_words = [w.lower() for w in re.findall(r"\w+", text) if w.lower() not in STOPWORDS]
    if not q_words or not t_words:
        return 0.0
    matches = sum(1 for w in q_words if w in t_words)
    return matches / len(q_words)


def answer_question(index: Dict[str, List[Dict]], question: str) -> Dict:
    """
    Return either {'refusal': REFUSAL_TEMPLATE} or {'answer': str, 'citation': {file, section}, 'score': float}
    """
    best = None  # tuple(score, filename, section, text)
    # find best per-document
    for filename, entries in index.items():
        best_in_doc = (0.0, None, None)
        for ent in entries:
            s = score_text(question, ent.get("text", ""))
            if s > best_in_doc[0]:
                best_in_doc = (s, ent.get("section"), ent.get("text"))

        if best_in_doc[0] > 0 and (best is None or best_in_doc[0] > best[0]):
            best = (best_in_doc[0], filename, best_in_doc[1], best_in_doc[2])

    # No good match
    if not best or best[0] < 0.25:
        return {"refusal": REFUSAL_TEMPLATE}

    # Check if another document has a near-equal score -> ambiguous
    top_score = best[0]
    top_doc = best[1]
    close_docs = 0
    for filename, entries in index.items():
        if filename == top_doc:
            continue
        # compute best in that doc
        best_other = 0.0
        for ent in entries:
            s = score_text(question, ent.get("text", ""))
            if s > best_other:
                best_other = s
        if best_other >= 0.9 * top_score and best_other >= 0.25:
            close_docs += 1

    if close_docs > 0:
        return {"refusal": REFUSAL_TEMPLATE}

    # return single-source answer
    _, filename, section, text = best
    # ensure no hedging words in the output
    hedging_phrases = ["while not explicitly covered", "typically", "generally understood", "it is common practice", "may be", "might be"]
    answer_text = text.strip()
    for p in hedging_phrases:
        answer_text = answer_text.replace(p, "")

    citation = {"filename": filename, "section": section}
    return {"answer": answer_text, "citation": citation, "score": float(best[0])}


def run_interactive(index: Dict[str, List[Dict]]):
    print("UC-X — Ask my documents. Type 'exit' to quit.")
    while True:
        try:
            q = input("Question: ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break
        res = answer_question(index, q)
        if "refusal" in res:
            print(res["refusal"])
        else:
            ans = res["answer"]
            c = res["citation"]
            print(f"{ans}\n({c['filename']}, {c['section']})")


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI")
    parser.add_argument("--files", nargs="*", default=[
        "data/policy-documents/policy_hr_leave.txt",
        "data/policy-documents/policy_it_acceptable_use.txt",
        "data/policy-documents/policy_finance_reimbursement.txt",
    ], help="Policy files to load")
    parser.add_argument("--question", help="Ask a single question and exit")
    args = parser.parse_args()

    index, errors = retrieve_documents(args.files)
    if errors:
        for e in errors:
            print("ERROR:", e)
    if args.question:
        res = answer_question(index, args.question)
        if "refusal" in res:
            print(res["refusal"])
        else:
            ans = res["answer"]
            c = res["citation"]
            print(f"{ans}\n({c['filename']}, {c['section']})")
        return

    run_interactive(index)


if __name__ == "__main__":
    main()
