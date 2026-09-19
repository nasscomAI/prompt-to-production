"""UC-X - Ask My Documents (single-source answers with citations)"""
import math
import os
import re

DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")
DOC_FILES = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]

REFUSAL = ("This question is not covered in the available policy documents\n"
           "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
           "Please contact the relevant department (HR, IT or Finance) for guidance.")

STOP = set("a an the is are am be to of for on in at by or and can could i my me we our you your do does did "
           "what which who how when where why with from as it its this that there any if not no than then "
           "should would will may must have has had get use used using about work working file files".split())
SYNONYMS = {"phone": ["device"], "phones": ["device"], "smartphone": ["device"], "laptop": ["device"],
            "laptops": ["device"], "slack": ["software"], "app": ["software"], "apps": ["software"],
            "application": ["software"], "wfh": ["work-from-home"], "da": ["daily", "allowance"]}
PHRASES = {"leave without pay": "lwp"}
SCORE_MIN = 3.0      # below this the question is treated as not covered
CLOSE_RATIO = 0.7    # extra clauses (same document only) must score at least this share of the best


def stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "al", "s", "e"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def tokens(text: str) -> list:
    out = []
    text = text.lower()
    for p, r in PHRASES.items():
        text = text.replace(p, r)
    for w in re.findall(r"[a-z0-9\-]+", text):
        if w in STOP:
            continue
        if w in SYNONYMS:
            out.extend(stem(x) for x in SYNONYMS[w])
        else:
            out.append(stem(w))
    return out


def retrieve_documents() -> list:
    """Load all 3 policies; index every clause as {doc, section, text, tokens}."""
    index = []
    for name in DOC_FILES:
        path = os.path.join(DOC_DIR, name)
        try:
            with open(path, encoding="utf-8-sig") as f:
                lines = f.read().splitlines()
        except OSError as e:
            raise SystemExit(f"Cannot load {name}: {e}")
        clause = None
        for line in lines:
            m = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
            if m:
                clause = {"doc": name, "section": m.group(1), "text": m.group(2)}
                index.append(clause)
            elif clause and line.startswith(" ") and line.strip():
                clause["text"] += " " + line.strip()
            elif line.startswith("═"):
                clause = None
    if not index:
        raise SystemExit("No clauses found in policy documents.")
    df = {}
    for c in index:
        c["tokens"] = set(tokens(c["text"]))
        for t in c["tokens"]:
            df[t] = df.get(t, 0) + 1
    n = len(index)
    avg = sum(len(c["tokens"]) for c in index) / n
    for c in index:
        norm = 1.2 * (0.25 + 0.75 * len(c["tokens"]) / avg)
        c["idf"] = {t: math.log(1 + n / df[t]) * 2.2 / (1 + norm) for t in c["tokens"]}
    return index


def answer_question(question: str, index: list) -> str:
    """Return a single-source answer with citation, or the refusal template."""
    q = set(tokens(question))
    scored = []
    for c in index:
        hit = q & c["tokens"]
        scored.append((sum(c["idf"][t] for t in hit), c))
    scored.sort(key=lambda x: -x[0])
    best, top = scored[0]
    if best < SCORE_MIN:
        return REFUSAL
    picks = [c for s, c in scored[:4] if c["doc"] == top["doc"] and s >= CLOSE_RATIO * best]
    picks.sort(key=lambda c: tuple(int(x) for x in c["section"].split(".")))
    lines = [f"- {c['text']}  [{c['doc']}, section {c['section']}]" for c in picks]
    return "\n".join(lines)


def main():
    index = retrieve_documents()
    print("Ask My Documents (HR leave, IT acceptable use, Finance reimbursement). Type 'exit' to quit.")
    while True:
        try:
            q = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue
        print(answer_question(q, index))


if __name__ == "__main__":
    main()