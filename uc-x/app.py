"""
UC-X app.py — 'Ask My Documents' policy Q&A assistant.

Answers company policy questions using ONLY the three policy documents
listed in agents.md. Output is either a single-source factual answer with
citation (document name + section number), or the exact refusal template.

Skills implemented (see skills.md):
  - retrieve_documents: loads the 3 policy files, indexes by section number.
  - answer_question: searches the index, returns a single-source answer
    with citation OR the refusal template — never a cross-document blend.

Run:  python app.py
Single prompt:  python app.py -q "Can I carry forward unused annual leave?"
"""
import argparse
import os
import re
import sys

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

BASE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "data",
    "policy-documents",
)

STOPWORDS = set(
    """
    a an the this that these those is are was were be been being
    and or but if then than so for to of in on at by with from
    about against between through during before after above below
    can could would should will shall may might must do does did
    what which who whom whose when where why how not no nor
    i you he she it we they me him her us them my your his its
    our their our their as into over under again further once here
    there all any both each few more most other some such only own
    same too very s t just don now am have has had having been being
    use used using work works worked working
    """.split()
)

TOP_SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
SUB_SECTION_RE = re.compile(r"^(\d+)\.(\d+)\s+(.*)$")


def normalize_acronyms(text):
    """Expand acronyms used in the policy documents so keyword matching works."""
    text = re.sub(r"\bLWP\b", "Leave Without Pay", text)
    text = re.sub(r"\bDA\b", "Daily Allowance", text)
    return text


WORD_FORMS = {
    "approve": "approval",
    "approves": "approval",
    "approved": "approval",
    "claim": "claim",
    "claims": "claim",
    "claimed": "claim",
    "install": "install",
    "installs": "install",
    "installed": "install",
    "receipt": "receipt",
    "receipts": "receipt",
}


def tokenize(text):
    """Lowercase word tokens with acronym expansion, form folding, stopword removal."""
    words = re.findall(r"[a-z0-9]+", normalize_acronyms(text).lower())
    return [
        WORD_FORMS.get(w, w)
        for w in words
        if w not in STOPWORDS
    ]


def _parse_sections(lines):
    """Split a policy file into {number, title, body} entries."""
    sections = []
    current = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if all(ch == "\u2550" for ch in line):  # separator line (=== block)
            continue
        top = TOP_SECTION_RE.match(line)
        sub = SUB_SECTION_RE.match(line)
        if top is not None or sub is not None:
            if current is not None:
                sections.append(current)
            if top is not None:
                number = top.group(1)
                title = top.group(2).strip()
            else:
                number = "{}.{}".format(sub.group(1), sub.group(2))
                title = sub.group(3).strip()
            current = {"number": number, "title": title, "body": ""}
        else:
            if current is not None:
                current["body"] += (" " + line) if current["body"] else line
    if current is not None:
        sections.append(current)
    return sections


def retrieve_documents():
    """Skill 1: load all policy files; index by document name + section number.

    Missing/unreadable files are reported and skipped; processing continues
    with the documents that did load.
    """
    documents = []
    failed = []
    for name in DOC_FILES:
        path = os.path.join(BASE_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            failed.append("{} ({})".format(name, type(exc).__name__))
            continue
        sections = _parse_sections(content.splitlines())
        documents.append({"name": name, "sections": sections})
    if failed:
        print("WARNING: could not load: {}".format(", ".join(failed)))
    if not documents:
        raise SystemExit("No policy documents could be loaded.")
    return documents


def _score_section(question_tokens, section):
    """Keyword match score: title hits weigh more than body hits."""
    qset = set(question_tokens)
    title_hits = len(set(tokenize(section["title"])) & qset)
    body_hits = len(set(tokenize(section["body"])) & qset)
    return 3 * title_hits + 1 * body_hits


def answer_question(documents, question):
    """Skill 2: return a single-source answer + citation, or the refusal template.

    Rule: if the best matches span two different documents (and the second
    document scores at least half as high as the best), refuse rather than
    blend. If nothing matches, refuse.
    """
    q_tokens = tokenize(question)
    ranked = []
    for doc in documents:
        for section in doc["sections"]:
            score = _score_section(q_tokens, section)
            if score > 0:
                ranked.append((score, doc["name"], section))
    ranked.sort(key=lambda item: item[0], reverse=True)

    if not ranked:
        return REFUSAL_TEMPLATE

    best_score, best_doc, best_section = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None
    if second is not None:
        s_score, s_doc, _ = second
        if s_doc != best_doc and s_score > best_score * 0.5:
            return REFUSAL_TEMPLATE

    citation = "{} — Section {}".format(best_doc, best_section["number"])
    text = best_section["title"]
    if best_section["body"]:
        text += "\n" + best_section["body"]
    return "{}\n\n{}".format(citation, text)


def _run_loop(documents):
    print("UC-X — Ask My Documents. Type a question, or 'quit'/'exit' to leave.")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            print()
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        print(answer_question(documents, question))


def main():
    parser = argparse.ArgumentParser(
        description="Policy document Q&A assistant (single-source answers only)."
    )
    parser.add_argument(
        "-q", "--question", help="Answer a single question and exit."
    )
    args = parser.parse_args()

    documents = retrieve_documents()
    if args.question:
        print(answer_question(documents, args.question))
    else:
        _run_loop(documents)


if __name__ == "__main__":
    main()