"""
UC-X app.py — Ask My Documents
Single-source Q&A over the three CMC policy documents.
Enforcement mirrored from agents.md:
  - never blends claims from two different documents into one answer
  - never hedges ("while not explicitly covered", "typically", ...)
  - uncovered questions get the exact refusal template
  - every factual claim cites source document name + section number
"""
import argparse
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, os.pardir, "data", "policy-documents")
DOCUMENTS = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt",
             "policy_finance_reimbursement.txt"]
TEAMS = {"policy_hr_leave.txt": "HR Department",
         "policy_it_acceptable_use.txt": "IT Department",
         "policy_finance_reimbursement.txt": "Finance Department"}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = ["while not explicitly covered", "typically",
                 "generally understood", "it is common practice"]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()\-]+)$")

STOPWORDS = set("""a an and are as at be by can for from how i in is it me may
my not of on or should the to do does did what when where which who whom why
will with would you your if there their they them we us our about into over
under please tell give show""".split())

SYNONYMS = {
    "phone": ["device", "devices", "personal"],
    "mobile": ["device", "devices"],
    "smartphone": ["device", "devices"],
    "laptop": ["corporate", "device", "devices", "computer"],
    "computer": ["corporate", "device", "devices"],
    "slack": ["software", "install", "installing"],
    "zoom": ["software", "install"],
    "app": ["software", "application"],
    "install": ["software", "installation"],
    "wfh": ["work", "home", "remote"],
    "encash": ["encashment"],
    "cash": ["encashment"],
    "payout": ["encashment"],
    "carryforward": ["carry", "forward"],
    "cert": ["certificate", "medical"],
    "sick": ["medical", "certificate"],
    "approve": ["approval", "approved"],
    "approver": ["approval", "approved"],
    "allowance": ["equipment", "reimbursable", "entitled"],
    "claim": ["claims", "claimed", "reimbursable", "reimbursement"],
    "receipt": ["receipts"],
    "meal": ["meals", "da", "daily", "allowance"],
    "da": ["daily", "allowance", "meals"],
    "perdiem": ["daily", "allowance", "da"],
    "wifi": ["network", "guest"],
    "password": ["passwords"],
    "gadgets": ["device", "devices"],
}


def _read_text(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def retrieve_documents(data_dir=DATA_DIR):
    """
    Load all 3 policy files and index them by document name + section number.
    Returns {doc: [{"number","text","heading"}, ...]}.
    """
    index = {}
    for doc in DOCUMENTS:
        path = os.path.abspath(os.path.join(data_dir, doc))
        if not os.path.isfile(path):
            print("ERROR: policy document missing: %s" % path, file=sys.stderr)
            raise SystemExit(1)
        clauses = []
        heading = ""
        number = None
        buf = []

        def flush():
            if number is not None and buf:
                clauses.append({"number": number,
                                "text": re.sub(r"\s+", " ", " ".join(buf)).strip(),
                                "heading": heading})

        for line in _read_text(path).splitlines():
            stripped = line.strip()
            if stripped and all(ch in "═─=-—" for ch in stripped):
                continue
            clause_m = CLAUSE_RE.match(stripped)
            head_m = HEADING_RE.match(stripped)
            if clause_m:
                flush()
                number, buf = clause_m.group(1), [clause_m.group(2)]
            elif head_m:
                flush()
                number, buf = None, []
                heading = "%s. %s" % (head_m.group(1), head_m.group(2))
            elif number is not None and stripped:
                buf.append(stripped)
        flush()
        index[doc] = clauses
    return index


def _stem(token):
    token = token.lower()
    if len(token) > 4 and token.endswith("ing"):
        token = token[:-3]
    elif len(token) > 3 and token.endswith("es"):
        token = token[:-2]
    elif len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]
    return token


def _expand(tokens):
    expanded = set()
    for token in tokens:
        stem = _stem(token)
        expanded.add(stem)
        for key, extras in SYNONYMS.items():
            if _stem(key) == stem:
                expanded.update(_stem(extra) for extra in extras)
    return expanded


def _tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower())
            if t not in STOPWORDS]


def _score_clauses(question, index):
    query = _expand(_tokenize(question))
    df = {}
    for doc, clauses in index.items():
        for clause in clauses:
            clause["words"] = {_stem(w) for w in _tokenize(
                clause["text"] + " " + clause["heading"])}
            for word in clause["words"]:
                df[word] = df.get(word, 0) + 1

    total = sum(len(c) for c in index.values())
    scored = []
    for doc, clauses in index.items():
        for clause in clauses:
            score = 0.0
            matched = []
            for term in query:
                if term in clause["words"]:
                    idf = 1.0 + (total - df.get(term, 0)) / max(total, 1)
                    weight = 2.5 * idf if len(term) > 3 else 1.0 * idf
                    score += weight
                    matched.append(term)
            if matched:
                scored.append({"doc": doc, "number": clause["number"],
                               "text": clause["text"], "score": score,
                               "matched": matched})
    scored.sort(key=lambda s: -s["score"])
    return scored


def answer_question(question, index):
    """
    Search indexed documents; return a single-source cited answer or the
    exact refusal template. Never mixes two documents in one answer.
    """
    question = (question or "").strip()
    if not question:
        return REFUSAL_TEMPLATE.replace("[relevant team]",
                                        "the responsible department")

    scored = _score_clauses(question, index)
    if os.environ.get("UCX_DEBUG"):
        for s in scored[:6]:
            print("DEBUG %6.2f %s %s matched=%s"
                  % (s["score"], s["doc"], s["number"], s["matched"]),
                  file=sys.stderr)

    if not scored:
        return REFUSAL_TEMPLATE.replace("[relevant team]",
                                        "the responsible department")

    top = scored[0]
    best_by_doc = {}
    for s in scored:
        best_by_doc[s["doc"]] = max(best_by_doc.get(s["doc"], 0.0),
                                    s["score"])
    ranked_docs = sorted(best_by_doc.items(), key=lambda kv: -kv[1])
    second_doc, second_score = (ranked_docs[1] if len(ranked_docs) > 1
                                else (None, 0.0))

    MIN_SCORE = 4.5
    BLEND_RATIO = 0.75

    if top["score"] < MIN_SCORE:
        team = TEAMS.get(ranked_docs[0][0], "the responsible department") \
            if ranked_docs[0][1] >= 2.0 else "the responsible department"
        return REFUSAL_TEMPLATE.replace("[relevant team]", team)

    if second_doc is not None and second_score >= BLEND_RATIO * top["score"]:
        return REFUSAL_TEMPLATE.replace(
            "[relevant team]", "the responsible department")

    same_doc = [s for s in scored if s["doc"] == top["doc"]]
    support = [s for s in same_doc[1:]
               if s["score"] >= 0.55 * top["score"]][:2]
    chosen = [top] + support

    lines = ["Answer comes from a SINGLE source document: %s "
             "(no other document was used)." % top["doc"], ""]
    for s in chosen:
        lines.append("[%s | Section %s]" % (s["doc"], s["number"]))
        lines.append('"%s"' % s["text"])
        lines.append("")
    lines.append("Source citation: %s, Section %s%s." % (
        top["doc"], top["number"],
        (", Sections %s" % ", ".join(s["number"] for s in support))
        if support else ""))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-X Ask My Documents (single-source policy Q&A)")
    parser.add_argument("--ask", default=None,
                        help="Ask one question non-interactively, print the "
                             "answer, then exit (optional; plain 'python "
                             "app.py' starts interactive mode)")
    parser.add_argument("--docs-dir", dest="docs_dir", default=None,
                        help="Optional override for the policy document "
                             "directory")
    args = parser.parse_args()

    index = retrieve_documents(args.docs_dir or DATA_DIR)

    if args.ask is not None:
        print(answer_question(args.ask, index))
        return

    print("UC-X — Ask My Documents")
    print("Indexed documents:")
    for doc in DOCUMENTS:
        print("  - %s (%d sections)" % (doc, len(index[doc])))
    print("Type a question about HR leave, IT acceptable use, or finance "
          "reimbursement policy.")
    print("Type 'quit' or press Ctrl+C to exit.\n")
    while True:
        try:
            try:
                question = input("You> ").strip()
            except EOFError:
                print("\nGoodbye.")
                return
            if not question:
                continue
            if question.lower() in {"quit", "exit", "q"}:
                print("Goodbye.")
                return
            answer = answer_question(question, index)
            for phrase in HEDGE_PHRASES:
                if phrase in answer.lower():
                    print("INTERNAL ENFORCEMENT VIOLATION: hedge phrase '%s'"
                          % phrase, file=sys.stderr)
            print("\nAssistant>\n%s\n" % answer)
        except KeyboardInterrupt:
            print("\nGoodbye.")
            return


if __name__ == "__main__":
    main()
