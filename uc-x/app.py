"""
UC-X — Ask My Documents

Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

The failure this UC exists to prevent is not a wrong answer. It is a fluent,
confident answer assembled from two documents that individually say something
narrower — an answer that grants a permission neither document gives. So
retrieval here selects a DOCUMENT first and answers only from within it, and
treats "two documents look equally relevant" as a refusal rather than as a
tie to be broken.

Run (interactive):
    python app.py

Run all 7 README test questions non-interactively:
    python app.py --selftest
"""
import argparse
import math
import os
import re
import sys

DOC_DIR_DEFAULT = os.path.join("..", "data", "policy-documents")
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

SECTION_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ,\-/&()]+)\s*$")
RULE_RE = re.compile(r"^[═=\-_]{5,}\s*$")
ALIAS_RE = re.compile(r"([A-Za-z][A-Za-z\- ]{3,40}?)\s*\(([A-Z]{2,5})\)")

# --- Enforcement rule 4: checked by exact substring match on the final text --
BANNED_HEDGES = [
    "while not explicitly covered", "not explicitly", "typically",
    "generally", "usually", "it is common practice", "generally understood",
    "it is likely", "presumably", "in most organisations", "as a rule",
    "it would seem", "may be interpreted", "best practice", "commonly",
    "it appears", "one would expect", "in principle",
]

STOPWORDS = set("""
a an the is are was were be been being do does did can could may might must
shall should will would i you he she it we they me my your our their this
that these those of in on at to for from with without by as and or but if
what when where who whom which how why any some all no not there here about
into over under again further then once do i'm can't cant im use used using
get got have has had am
""".split())

# The [relevant team] placeholder is bound ONCE, globally. It never varies per
# question, because per-question variation is the gap through which hedging
# re-enters (enforcement rule 5).
RELEVANT_TEAM = "the HR, IT, or Finance department"

MIN_RELEVANCE = 2.0      # below this, nothing in the corpus is really on-topic
AMBIGUITY_MARGIN = 0.20  # second doc within 20% of the best -> refuse

# One shared word is a coincidence, not a topic. "What is the refund policy
# for parking fines?" overlaps the corpus only on "policy" -- a word in all
# three documents -- and answering it produced three confidently cited
# finance sections about travel pre-approval. Requiring two distinct matched
# terms costs some thin-but-genuine questions an answer, which is the correct
# direction of error for this UC.
MIN_MATCHED_TERMS = 2

# A section heading describes the neighbourhood, not the claim. Scoring
# heading terms at full weight let Finance section 5.2 (internet
# reimbursement) inherit "PHONE" from its heading "MOBILE PHONE AND INTERNET"
# and outrank the IT section that actually governs personal phone use.
# Headings still contribute -- "LEAVE WITHOUT PAY (LWP)" is how section 5.2
# is reachable from the words "leave without pay" -- but they cannot decide a
# document on their own.
HEADING_WEIGHT = 0.4


def stem(word):
    """Crude but symmetric suffix stripping, applied to corpus and question
    alike.

    Two failures made this necessary. 'mobile phones' was unreachable from
    'personal phone', and — worse — HR section 5.2 says "LWP requires
    approval" while the question asks "who approves", so the clause naming
    both required approvers shared no body token with the question at all and
    was reachable only through its section heading.
    """
    if len(word) > 4 and word.endswith("ies"):
        word = word[:-3] + "y"
    elif (len(word) > 4 and word.endswith("es")
          and word[:-2].endswith(("s", "x", "z", "ch", "sh"))):
        # Only strip a full "es" where English actually adds one (boxes,
        # expenses, batches). Stripping it indiscriminately turned "fines"
        # into "fin", which then collided with the finance form codes FIN-T1
        # and FIN-EXP1 and scored as a rare, highly specific match.
        word = word[:-2]
    elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]

    for suffix, minimum in (("ment", 7), ("ing", 6), ("ion", 6),
                            ("ed", 5), ("al", 6)):
        if len(word) > minimum and word.endswith(suffix):
            word = word[:-len(suffix)]
            break
    if len(word) > 4 and word.endswith("e"):
        word = word[:-1]
    return word


def build_refusal(documents):
    return (
        "This question is not covered in the available policy documents\n"
        "(%s).\n"
        "Please contact %s for guidance." % (", ".join(documents), RELEVANT_TEAM)
    )


def tokenize(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower())
            if w not in STOPWORDS and len(w) > 1]


def retrieve_documents(doc_dir):
    """Load the three policy files into a section index with an idf table."""
    sections = []
    documents = []
    missing = []

    for name in DOC_FILES:
        path = os.path.join(doc_dir, name)
        if not os.path.isfile(path):
            missing.append(name)
            continue
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()

        heading = ""
        current = None
        parsed = []

        def close(cur):
            if cur is not None:
                cur["text"] = re.sub(r"\s+", " ", " ".join(cur["parts"])).strip()
                del cur["parts"]
                if cur["text"]:
                    parsed.append(cur)

        for line in lines:
            if RULE_RE.match(line) or not line.strip():
                continue
            section_match = SECTION_RE.match(line)
            heading_match = HEADING_RE.match(line.strip())
            if section_match:
                close(current)
                current = {"doc": name, "number": section_match.group(1),
                           "heading": heading, "parts": [section_match.group(2)]}
            elif heading_match:
                close(current)
                current = None
                heading = heading_match.group(2).strip()
            elif current is not None and line.startswith(" "):
                current["parts"].append(line.strip())
        close(current)

        if not parsed:
            print("WARNING: %s parsed to zero numbered sections — excluded "
                  "from the index." % name)
            continue
        sections.extend(parsed)
        documents.append(name)

    if missing:
        print("WARNING: missing policy file(s): %s. The refusal template will "
              "list only the documents actually loaded." % ", ".join(missing))
    if not sections:
        raise SystemExit(
            "ERROR: no policy documents could be indexed from %s — refusing to "
            "start a session that would decline every question for the wrong "
            "reason." % doc_dir)

    # Acronym glossary, harvested from the documents' own definitions.
    aliases = {}
    corpus = " ".join(s["heading"] + " " + s["text"] for s in sections)
    for phrase, acronym in ALIAS_RE.findall(corpus):
        words = [w for w in re.findall(r"[A-Za-z]+", phrase)]
        tail = words[-len(acronym):] if len(words) >= len(acronym) else words
        initials = "".join(w[0].upper() for w in tail)
        if initials == acronym:
            aliases[acronym.lower()] = " ".join(w.lower() for w in tail)

    for section in sections:
        section["body_tokens"] = set(tokenize(section["text"]))
        # Heading terms the body does not already state, scored at
        # HEADING_WEIGHT rather than at full strength.
        section["head_tokens"] = (set(tokenize(section["heading"]))
                                  - section["body_tokens"])
        section["tokens"] = section["body_tokens"] | section["head_tokens"]

    # idf so that rare terms ("encashment", "reimbursement") outweigh common
    # ones ("policy", "employee") that appear in all three documents.
    total = len(sections)
    doc_freq = {}
    for section in sections:
        for token in set(section["tokens"]):
            doc_freq[token] = doc_freq.get(token, 0) + 1
    idf = dict((t, math.log(1.0 + total / float(c)))
               for t, c in doc_freq.items())

    return {"sections": sections, "documents": documents, "aliases": aliases,
            "idf": idf, "refusal": build_refusal(documents)}


def expand(tokens, aliases):
    """Add each acronym's expansion and each expansion's acronym.

    Matching is on the content words of the expansion, not the raw phrase:
    "leave without pay" reduces to {leav, pay} once 'without' is dropped as a
    stopword, so a question asking "who approves leave without pay" still
    reaches the clauses that only ever say LWP.
    """
    present = set(tokens)
    out = list(tokens)
    for acronym, phrase in aliases.items():
        phrase_tokens = set(tokenize(phrase))
        if acronym in present:
            out.extend(phrase_tokens)
        elif phrase_tokens and phrase_tokens <= present:
            out.append(acronym)
    return out


def score_section(section, q_tokens, idf):
    asked = set(q_tokens)
    body = sum(idf.get(t, 0.0) for t in asked if t in section["body_tokens"])
    head = sum(idf.get(t, 0.0) for t in asked if t in section["head_tokens"])
    return body + HEADING_WEIGHT * head


def answer_question(index, question):
    """Return a single-source cited answer, or the refusal template."""
    refusal = index["refusal"]
    diagnostics = {"doc_scores": {}, "margin": None, "top_sections": []}

    if not question or not question.strip():
        return {"mode": "refusal", "document": None, "sections": [],
                "text": refusal, "diagnostics": diagnostics,
                "reason": "empty question"}

    q_tokens = expand(tokenize(question), index["aliases"])
    if not q_tokens:
        return {"mode": "refusal", "document": None, "sections": [],
                "text": refusal, "diagnostics": diagnostics,
                "reason": "question contained no searchable terms"}

    asked = set(q_tokens)
    scored = []
    doc_terms = {}
    for section in index["sections"]:
        value = score_section(section, q_tokens, index["idf"])
        # What question terms does this DOCUMENT account for anywhere in its
        # text? Used below to tell a genuine second source from a document
        # that merely repeats some of the leader's vocabulary.
        covered = asked & section["tokens"]
        if covered:
            doc_terms.setdefault(section["doc"], set()).update(covered)
        if value > 0:
            scored.append((value, section))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["doc"],
                                  pair[1]["number"]))

    # A document's score is its single best section. Summing sections would
    # reward long documents rather than relevant ones.
    doc_best = {}
    for value, section in scored:
        if section["doc"] not in doc_best or value > doc_best[section["doc"]][0]:
            doc_best[section["doc"]] = (value, section)
    diagnostics["doc_scores"] = dict((d, round(v[0], 2))
                                     for d, v in doc_best.items())

    if not doc_best:
        return {"mode": "refusal", "document": None, "sections": [],
                "text": refusal, "diagnostics": diagnostics,
                "reason": "no section matched any question term"}

    ranked = sorted(doc_best.items(), key=lambda kv: -kv[1][0])
    best_doc, (best_score, _) = ranked[0]

    # Enforcement rule 5: a weak match is a refusal, not a hedged answer.
    if best_score < MIN_RELEVANCE:
        return {"mode": "refusal", "document": None, "sections": [],
                "text": refusal, "diagnostics": diagnostics,
                "reason": "best score %.2f below relevance threshold %.2f"
                          % (best_score, MIN_RELEVANCE)}

    matched = doc_terms.get(best_doc, set())
    diagnostics["matched_terms"] = sorted(matched)
    if len(matched) < MIN_MATCHED_TERMS:
        return {"mode": "refusal", "document": None, "sections": [],
                "text": refusal, "diagnostics": diagnostics,
                "reason": "only %d question term(s) matched (%s); %d required "
                          "— a single shared word is a coincidence, not a topic"
                          % (len(matched), ", ".join(sorted(matched)) or "-",
                             MIN_MATCHED_TERMS)}

    # Enforcement rule 2: near-tie between documents is a refusal, never a
    # merge and never an arbitrary pick.
    #
    # A close score alone is not ambiguity. A document is only a genuine
    # alternative source if it accounts for something the leader does not.
    # Asked "can I install Slack on my work laptop", the Finance policy scores
    # close only because it also mentions laptops -- it covers no question
    # term the IT policy misses, so it offers less of the same answer, not a
    # competing one. Refuse when the rival is both close AND exclusive.
    leader_terms = doc_terms.get(best_doc, set())
    if len(ranked) > 1:
        second_doc, (second_score, _) = ranked[1]
        margin = (best_score - second_score) / best_score
        exclusive = doc_terms.get(second_doc, set()) - leader_terms
        diagnostics["margin"] = round(margin, 3)
        diagnostics["rival_exclusive_terms"] = sorted(exclusive)
        if margin < AMBIGUITY_MARGIN and exclusive:
            return {"mode": "refusal", "document": None, "sections": [],
                    "text": refusal, "diagnostics": diagnostics,
                    "reason": "cross-document ambiguity: %s %.2f vs %s %.2f "
                              "(margin %.1f%% < %.0f%%) and %s uniquely covers "
                              "%s"
                              % (best_doc, best_score, second_doc,
                                 second_score, margin * 100,
                                 AMBIGUITY_MARGIN * 100, second_doc,
                                 ", ".join(sorted(exclusive)))}

    # Enforcement rule 1: from here on, only best_doc is readable.
    in_doc = [(v, s) for v, s in scored if s["doc"] == best_doc]
    cutoff = in_doc[0][0] * 0.5
    chosen = [(v, s) for v, s in in_doc if v >= cutoff][:3]
    chosen.sort(key=lambda pair: [int(p) for p in pair[1]["number"].split(".")])
    diagnostics["top_sections"] = [s["number"] for _, s in chosen]

    lines = ["Source: %s (single-source answer)" % best_doc, ""]
    for _, section in chosen:
        # Enforcement rule 3: no sentence without a section citation.
        lines.append("  [%s section %s] %s"
                     % (best_doc, section["number"], section["text"]))
    text = "\n".join(lines)

    # Enforcement rule 4: hedge check runs on the assembled string, so it
    # cannot be bypassed by how the answer was built.
    lowered = text.lower()
    for hedge in BANNED_HEDGES:
        if hedge in lowered:
            return {"mode": "refusal", "document": None, "sections": [],
                    "text": refusal, "diagnostics": diagnostics,
                    "reason": "draft answer contained banned hedge %r" % hedge}

    return {"mode": "answer", "document": best_doc,
            "sections": [s["number"] for _, s in chosen], "text": text,
            "diagnostics": diagnostics, "reason": "single-source match"}


TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?",
     "HR policy section 2.6 — exact limit, exact forfeiture date"),
    ("Can I install Slack on my work laptop?",
     "IT policy section 2.3 — requires written IT approval"),
    ("What is the home office equipment allowance?",
     "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only"),
    ("Can I use my personal phone to access work files when working from home?",
     "Single-source IT answer OR clean refusal — must NOT blend"),
    ("What is the company view on flexible working culture?",
     "Refusal template — not in any document"),
    ("Can I claim DA and meal receipts on the same day?",
     "Finance section 2.6 — NO, explicitly prohibited"),
    ("Who approves leave without pay?",
     "HR section 5.2 — Department Head AND HR Director, both required"),
]


def selftest(index, verbose=True):
    print("=" * 78)
    print("UC-X SELF TEST — the 7 README questions")
    print("=" * 78)
    blended = 0
    hedged = 0
    for number, (question, expected) in enumerate(TEST_QUESTIONS, start=1):
        result = answer_question(index, question)
        print("")
        print("Q%d. %s" % (number, question))
        print("    expected: %s" % expected)
        print("    -> mode=%s  document=%s  sections=%s"
              % (result["mode"], result["document"] or "-",
                 ", ".join(result["sections"]) or "-"))
        if verbose:
            print("    routing : %s" % result["reason"])
            print("    scores  : %s" % result["diagnostics"]["doc_scores"])
        for line in result["text"].splitlines():
            print("    | %s" % line)
        if result["mode"] == "answer" and result["document"] is None:
            blended += 1
        lowered = result["text"].lower()
        if any(h in lowered for h in BANNED_HEDGES):
            hedged += 1
    print("")
    print("=" * 78)
    print("answers citing more than one document : %d" % blended)
    print("answers containing a hedging phrase   : %d" % hedged)
    print("=" * 78)
    return blended == 0 and hedged == 0


def repl(index):
    print("=" * 78)
    print("Ask My Documents — UC-X")
    print("Indexed: %s" % ", ".join(index["documents"]))
    print("Every answer comes from ONE document with section citations, or is")
    print("declined. Type 'quit' to exit, 'why' to see the last routing call.")
    print("=" * 78)
    last = None
    while True:
        try:
            question = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            return
        if question.lower() in ("quit", "exit", "q"):
            print("Session ended.")
            return
        if question.lower() == "why":
            if last is None:
                print("No question asked yet.")
            else:
                print("routing: %s" % last["reason"])
                print("scores : %s" % last["diagnostics"]["doc_scores"])
                print("margin : %s" % last["diagnostics"]["margin"])
            continue
        if not question:
            print("Please type a question.")
            continue
        last = answer_question(index, question)
        print("")
        print(last["text"])


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default=DOC_DIR_DEFAULT,
                        help="Directory holding the three policy .txt files")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions and exit")
    parser.add_argument("--ask", default=None,
                        help="Ask a single question and exit")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)

    if args.selftest:
        sys.exit(0 if selftest(index) else 1)
    if args.ask:
        result = answer_question(index, args.ask)
        print(result["text"])
        print("")
        print("[routing: %s]" % result["reason"])
        return
    repl(index)


if __name__ == "__main__":
    main()
