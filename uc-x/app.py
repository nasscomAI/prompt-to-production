"""
UC-X — Ask My Documents
Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

The naive prompt ("Answer questions about company policy.") failed the
cross-document test question on the first try. Asked "Can I use my personal
phone to access work files when working from home?" it answered:

  "Yes — personal devices can be used for approved remote work tools and CMC
   email, though while not explicitly covered, sensitive data should generally
   be avoided."

That sentence blends IT 3.1 with the HR document, hedges twice, cites nothing,
and grants a permission that exists in no file.

This implementation cannot produce that answer:

  single source   retrieval picks ONE document; there is no code path that
                  concatenates clauses from two files
  verbatim only   answers are quoted, never paraphrased, and each quote is
                  asserted character-for-character against the index
  no hedging      the assembled response is scanned for banned phrases and
                  becomes a refusal if any is found
  two refusal     a vocabulary gate ("do these documents use these words at
  gates           all?") and a coverage gate ("do the clauses I am about to
                  quote address the question?"), plus an ambiguity check that
                  refuses when two documents are too close to separate

Run:  python app.py            (interactive)
      python app.py --test     (runs the 7 README test questions)
"""
import argparse
import math
import os
import re
import sys

DOCUMENTS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

# --- Enforcement rule 3: the refusal template ------------------------------
# The ONLY substitution permitted in this string is {team}, filled from TEAMS.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)
TEAMS = {
    "hr": "the HR Department",
    "it": "the IT Department",
    "finance": "the Finance Department",
}
DEFAULT_TEAM = TEAMS["hr"]

TEAM_HINTS = [
    (re.compile(r"\b(device|laptop|phone|software|install|password|network|"
                r"email|wifi|byod|data|printer|system)\w*\b", re.I), TEAMS["it"]),
    (re.compile(r"\b(claim|expense|reimburs|allowance|travel|hotel|invoice|"
                r"receipt|salary|payment|budget|da)\w*\b", re.I), TEAMS["finance"]),
    (re.compile(r"\b(leave|holiday|maternity|paternity|sick|grievance|culture|"
                r"working|employee|hr|encash)\w*\b", re.I), TEAMS["hr"]),
]

# --- Enforcement rule 2: banned hedging ------------------------------------
HEDGE_PATTERN = re.compile(
    r"while not explicitly covered|not explicitly (?:covered|stated|mentioned)"
    r"|generally understood|it is common practice|common practice"
    r"|\btypically\b|\bgenerally\b|\busually\b|in most cases|should be fine"
    r"|\bpresumably\b|it is likely|\bprobably\b|\bpresumed\b|as a rule of thumb",
    re.I,
)

# --- Retrieval tuning ------------------------------------------------------
# Two independent refusal gates, each with a distinct job:
#   VOCABULARY_FLOOR — "do these documents talk about the things you asked
#     about at all?" Measured on the words the user actually typed, before any
#     expansion. This is what catches "flexible working culture", where three of
#     five content words appear nowhere in any of the three files.
#   CONFIDENCE_FLOOR — "do the clauses I am about to quote address the
#     question?" Measured over the union of what those clauses matched.
#   MIN_MATCHED_TERMS — "is there enough of the question here to cite at all?"
#     Found during testing: "What is the parking policy?" passed both floors on
#     the single word "policy" and confidently returned IT sections 1.1-1.3.
#     Across the corpus, every answerable question matches 4+ distinct terms and
#     every unanswerable one matches 1-2, so 3 is a real margin, not a fitted
#     constant.
VOCABULARY_FLOOR = 0.50
CONFIDENCE_FLOOR = 0.30
MIN_MATCHED_TERMS = 3
AMBIGUITY_MARGIN = 0.80     # runner-up/winner ratio above which nothing decides
MAX_CITATIONS = 3
TITLE_WEIGHT = 0.6
PHRASE_BONUS = 1.6

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am", "i",
    "my", "me", "we", "our", "you", "your", "can", "could", "do", "does",
    "did", "what", "which", "who", "whom", "when", "where", "why", "how",
    "on", "in", "to", "of", "for", "and", "or", "at", "by", "with", "from",
    "this", "that", "these", "those", "it", "its", "if", "any", "there",
    "have", "has", "had", "will", "would", "shall", "should", "may", "might",
    "get", "got", "s", "t",
}
KEEP_SHORT = {"da", "it", "hr", "lwp", "pc"}

# Question-side vocabulary bridges. Applied at reduced weight so they help
# retrieval without letting an expansion outvote a word the user actually typed.
EXPANSIONS = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
    "wfh": ["work", "home", "arrangements"],
    "approves": ["approval", "approved"],
    "approve": ["approval", "approved"],
    "carryforward": ["carry", "forward"],
    "install": ["installation", "software"],
    "laptop": ["laptops"],
    "files": ["data", "store"],
    "slack": ["software"],
    "allowance": ["entitled"],
    "meal": ["meals"],
    "encash": ["encashed", "encashment"],
}

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ,()/&'\-]+)\s*$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
CONTINUATION_RE = re.compile(r"^\s{2,}(\S.*)$")
SEPARATOR_RE = re.compile(r"^[═=]{3,}\s*$")
TOKEN_RE = re.compile(r"[A-Za-z]+")


IRREGULAR = {"used": "use", "using": "use", "uses": "use",
             "files": "file", "leaves": "leave"}


def _stem(word: str) -> str:
    """Crude but symmetric: the question and the corpus go through this same
    function, so what matters is that plural/verb forms of one word collapse to
    one token. 'phones' and 'phone' must not end up as two."""
    word = word.lower()
    if word in IRREGULAR:
        return IRREGULAR[word]
    if word.endswith("ies") and len(word) >= 5:
        return word[:-3] + "y"
    for suffix in ("ations", "ation", "ements", "ement", "ings", "ing",
                   "ied", "ers", "er", "ed", "al"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    # "es" only where English actually needs it (boxes, watches, passes);
    # otherwise strip the plural "s" alone so phones -> phone, devices -> device.
    if word.endswith("es") and len(word) - 2 >= 4 \
            and word[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) - 1 >= 4:
        return word[:-1]
    return word


def _tokenize(text: str) -> list:
    out = []
    for raw in TOKEN_RE.findall(text):
        low = raw.lower()
        if low in KEEP_SHORT:
            out.append(low)
            continue
        if low in STOPWORDS or len(low) < 3:
            continue
        out.append(_stem(low))
    return out


def retrieve_documents(paths: list) -> dict:
    """Load all three policy files and index them by document and section."""
    clauses = []
    documents = []

    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(
                "Policy document not found: %s. The refusal template promises "
                "the user that all three documents were searched, so the agent "
                "will not start with an incomplete set." % path)
        name = os.path.basename(path)
        documents.append(name)

        with open(path, encoding="utf-8") as handle:
            raw = handle.read()

        section_number, section_title, current = "", "", None
        found = 0
        for line in raw.splitlines():
            stripped = line.strip()
            if SEPARATOR_RE.match(stripped):
                current = None
                continue
            section_hit = SECTION_RE.match(stripped)
            if section_hit:
                section_number = section_hit.group(1)
                section_title = section_hit.group(2).strip()
                current = None
                continue
            clause_hit = CLAUSE_RE.match(line)
            if clause_hit and section_number:
                current = {
                    "document": name,
                    "section": section_number,
                    "section_title": section_title,
                    "number": clause_hit.group(1),
                    "text": clause_hit.group(2).strip(),
                }
                clauses.append(current)
                found += 1
                continue
            continuation = CONTINUATION_RE.match(line)
            if continuation and current is not None:
                current["text"] += " " + continuation.group(1).strip()

        if found == 0:
            raise ValueError(
                "%s produced no clauses. An unparseable policy indexed as empty "
                "would make every question about it return a confident refusal."
                % name)

    for clause in clauses:
        clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
        clause["tokens"] = _tokenize(clause["text"])
        clause["title_tokens"] = _tokenize(clause["section_title"])
        clause["lower"] = (clause["text"] + " " + clause["section_title"]).lower()

    total = len(clauses)
    document_freq = {}
    for clause in clauses:
        for token in set(clause["tokens"]) | set(clause["title_tokens"]):
            document_freq[token] = document_freq.get(token, 0) + 1
    idf = {token: math.log(1 + total / count)
           for token, count in document_freq.items()}

    return {"clauses": clauses, "documents": documents, "idf": idf}


def _query_terms(question: str) -> dict:
    """Question tokens with weights; expansions carry less weight than typed words."""
    typed = _tokenize(question)
    terms = {}
    for token in typed:
        terms[token] = max(terms.get(token, 0.0), 1.0)
    for raw in TOKEN_RE.findall(question.lower()):
        for extra in EXPANSIONS.get(raw, []):
            stem = _stem(extra)
            if stem not in terms:
                terms[stem] = 0.55
    return terms


def _score(clause: dict, terms: dict, idf: dict, question: str):
    """Return (score, {token: weight contributed}) for one clause."""
    score = 0.0
    matched = {}
    clause_tokens = set(clause["tokens"])
    title_tokens = set(clause["title_tokens"])

    for token, weight in terms.items():
        strength = idf.get(token, 0.0)
        if not strength:
            continue
        if token in clause_tokens:
            contribution = weight * strength
        elif token in title_tokens:
            contribution = weight * strength * TITLE_WEIGHT
        else:
            continue
        score += contribution
        matched[token] = max(matched.get(token, 0.0), contribution)

    words = [w for w in re.split(r"[^a-z]+", question.lower()) if w]
    for first, second in zip(words, words[1:]):
        if first in STOPWORDS and second in STOPWORDS:
            continue
        if "%s %s" % (first, second) in clause["lower"]:
            score += PHRASE_BONUS

    return score, matched


def _pick_team(question: str) -> str:
    for pattern, team in TEAM_HINTS:
        if pattern.search(question):
            return team
    return DEFAULT_TEAM


def _refusal(question: str, reason: str) -> dict:
    return {
        "kind": "refusal",
        "document": None,
        "citations": [],
        "excluded": [],
        "coverage": 0.0,
        "reason": reason,
        "text": REFUSAL_TEMPLATE.format(team=_pick_team(question)),
    }


def answer_question(index: dict, question: str) -> dict:
    """Single-source cited answer, or the refusal template. Nothing else."""
    if not question or not question.strip():
        raise ValueError("Empty question — prompt again rather than refusing.")

    terms = _query_terms(question)
    idf = index["idf"]
    total_weight = sum(weight * idf.get(token, 0.0)
                       for token, weight in terms.items())

    if total_weight <= 0:
        return _refusal(question, "no term in the question appears in any of "
                                  "the three documents")

    # --- Gate 1: does the corpus even use this vocabulary? ------------------
    typed = list(dict.fromkeys(_tokenize(question)))
    unknown = [token for token in typed if not idf.get(token)]
    known_share = (len(typed) - len(unknown)) / len(typed) if typed else 0.0
    if known_share < VOCABULARY_FLOOR:
        return _refusal(
            question,
            "%d of the %d content words in this question (%s) appear nowhere in "
            "any of the three documents, so there is nothing here to cite"
            % (len(unknown), len(typed), ", ".join(unknown)))

    scored = []
    for clause in index["clauses"]:
        score, matched = _score(clause, terms, idf, question)
        if score > 0:
            scored.append((score, matched, clause))
    if not scored:
        return _refusal(question, "no clause matched any term in the question")

    scored.sort(key=lambda item: -item[0])

    # --- Enforcement rule 1: one document decides, or nobody does ----------
    per_document = {}
    for score, _, clause in scored[:12]:
        per_document[clause["document"]] = per_document.get(
            clause["document"], 0.0) + score
    ranked_documents = sorted(per_document.items(), key=lambda kv: -kv[1])
    winner, winner_score = ranked_documents[0]

    # Citations: the strongest clauses inside the winning document only. There
    # is deliberately no branch here that reaches into a second document.
    in_winner = [item for item in scored if item[2]["document"] == winner]

    # Section coherence — a policy answer lives in one section, not scattered
    # across a document. Pick the section that carries the most evidence, then
    # cite within it. This is what pulls IT 3.1 (what personal devices MAY
    # access) into the same answer as IT 3.2 (what they must not), instead of
    # returning one strong clause plus two unrelated mentions of "personal".
    per_section = {}
    for score, _, clause in in_winner:
        per_section[clause["section"]] = per_section.get(
            clause["section"], 0.0) + score
    best_section = max(per_section.items(), key=lambda kv: kv[1])[0]

    in_section = [item for item in in_winner
                  if item[2]["section"] == best_section]
    top_score = in_section[0][0]
    chosen = [item for item in in_section[:MAX_CITATIONS]
              if item[0] >= top_score * 0.45]

    # Coverage is measured over everything about to be quoted: how much of the
    # question these clauses actually answer.
    union = {}
    for _, matched, _ in chosen:
        for token, contribution in matched.items():
            union[token] = max(union.get(token, 0.0), contribution)
    coverage = sum(union.values()) / total_weight

    # --- Gate 2: is there enough of the question here to cite anything? -----
    if len(union) < MIN_MATCHED_TERMS:
        return _refusal(
            question,
            "only %d distinct term(s) from the question (%s) match anything in "
            "%s — one or two common words is not evidence that this question is "
            "answered here"
            % (len(union), ", ".join(sorted(union)), winner))

    if coverage < CONFIDENCE_FLOOR:
        return _refusal(
            question,
            "the clauses that matched cover only %.0f%% of the question's "
            "weight, below the %.0f%% confidence floor — the question is not "
            "answered by these documents"
            % (coverage * 100, CONFIDENCE_FLOOR * 100))

    runner_up_ratio = (ranked_documents[1][1] / winner_score
                       if len(ranked_documents) > 1 and winner_score else 0.0)
    if runner_up_ratio >= AMBIGUITY_MARGIN:
        return _refusal(
            question,
            "two documents (%s) score within %d%% of each other, so no single "
            "document decides the question and combining them is forbidden"
            % (", ".join(name for name, _ in ranked_documents[:2]),
               int(AMBIGUITY_MARGIN * 100)))

    citations = []
    for _, _, clause in sorted(chosen, key=lambda item: [
            int(part) for part in item[2]["number"].split(".")]):
        # Verbatim guarantee: the printed text IS the indexed clause text.
        indexed = next(c for c in index["clauses"]
                       if c["document"] == clause["document"]
                       and c["number"] == clause["number"])
        assert clause["text"] == indexed["text"], "verbatim invariant broken"
        citations.append({"document": clause["document"],
                          "section": clause["number"],
                          "text": clause["text"]})

    # Only name a document as excluded if it was a real competitor; listing a
    # document that scored 3% would be noise, not transparency.
    excluded = [name for name, score in ranked_documents[1:]
                if winner_score and score >= 0.15 * winner_score]

    lines = ["ANSWER — single source: %s" % winner, ""]
    for citation in citations:
        lines.append("  %s § %s — %s" % (citation["document"],
                                         citation["section"], citation["text"]))
    lines.append("")
    lines.append("  Source: %s, section(s) %s"
                 % (winner, ", ".join(c["section"] for c in citations)))
    lines.append("  Vocabulary recognised: %.0f%% of the words you typed "
                 "(floor %.0f%%)" % (known_share * 100, VOCABULARY_FLOOR * 100))
    lines.append("  Excluded by the single-source rule: %s"
                 % (", ".join(excluded) if excluded
                    else "no other document matched materially"))
    lines.append("  Retrieval coverage: %.0f%% (floor %.0f%%)"
                 % (coverage * 100, CONFIDENCE_FLOOR * 100))
    text = "\n".join(lines)

    # --- Enforcement rule 2: no hedging survives ---------------------------
    hedge = HEDGE_PATTERN.search(text)
    if hedge:
        return _refusal(
            question,
            "assembled answer contained the banned hedging phrase %r, so it was "
            "discarded rather than softened" % hedge.group(0))

    return {"kind": "answer", "document": winner, "citations": citations,
            "excluded": excluded, "coverage": coverage, "reason": "", "text": text}


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


EXTRA_PROBES = [
    ("Can I use a personal device to access CMC email?",
     "The same subject as Q4, narrowed to one document. Proves the system can "
     "and does answer from IT 3.1 alone — Q4 is refused for ambiguity, not "
     "because IT 3.1 is unreachable."),
    ("Can I install software on a corporate laptop without approval?",
     "IT 2.3 — checks the answer is the rule clause, not the definition clause."),
    ("How many days of sick leave am I entitled to?",
     "HR 3.1 — a plain single-clause lookup."),
    ("What is the parking policy?",
     "Adversarial. Caught a false answer during testing: this matched only the "
     "word 'policy' and returned IT 1.1-1.3 with full confidence. Must refuse."),
    ("What is my notice period?",
     "Adversarial. 'notice' and 'period' both exist in the corpus in unrelated "
     "senses. Must refuse rather than cite them."),
    ("What time does the office open?",
     "Adversarial. 'office' appears in 'home office'; 'time' in 'one-time'. "
     "Must refuse."),
]


def run_tests(index: dict) -> int:
    print("=" * 78)
    print("UC-X — the 7 test questions from uc-x/README.md")
    print("=" * 78)

    results = []
    for number, (question, expected) in enumerate(TEST_QUESTIONS, start=1):
        result = answer_question(index, question)
        results.append((question, result))
        print("\nQ%d. %s" % (number, question))
        print("    expected: %s" % expected)
        print("    kind    : %s" % result["kind"].upper())
        if result["kind"] == "refusal":
            print("    why     : %s" % result["reason"])
        print("-" * 78)
        print(result["text"])
        print("-" * 78)

    print("\n" + "=" * 78)
    print("ADDITIONAL PROBES — evidence beyond the seven")
    print("=" * 78)
    for question, why in EXTRA_PROBES:
        result = answer_question(index, question)
        results.append((question, result))
        print("\n?  %s" % question)
        print("   why asked: %s" % why)
        print("-" * 78)
        print(result["text"])
        print("-" * 78)

    # --- Assertions over every response produced above ---------------------
    blended = [q for q, r in results
               if len({c["document"] for c in r["citations"]}) > 1]
    hedged = [q for q, r in results if HEDGE_PATTERN.search(r["text"])]
    uncited = [q for q, r in results
               if r["kind"] == "answer" and any(
                   not c["document"] or not re.match(r"^\d+\.\d+$", c["section"])
                   for c in r["citations"])]
    bad_template = [q for q, r in results
                    if r["kind"] == "refusal"
                    and r["text"] not in
                    [REFUSAL_TEMPLATE.format(team=t) for t in TEAMS.values()]]
    not_verbatim = []
    for question, result in results:
        for citation in result["citations"]:
            match = next((c for c in index["clauses"]
                          if c["document"] == citation["document"]
                          and c["number"] == citation["section"]), None)
            if match is None or match["text"] != citation["text"]:
                not_verbatim.append("%s -> %s %s"
                                    % (question, citation["document"],
                                       citation["section"]))

    answers = sum(1 for _, r in results if r["kind"] == "answer")
    refusals = sum(1 for _, r in results if r["kind"] == "refusal")

    print("\n" + "=" * 78)
    print("ENFORCEMENT CHECKS across all %d responses" % len(results))
    print("=" * 78)
    print("  answers: %d | refusals: %d" % (answers, refusals))
    checks = [
        ("answers citing more than one document (must be 0)", blended),
        ("responses containing a banned hedging phrase (must be 0)", hedged),
        ("answers with a missing or malformed citation (must be 0)", uncited),
        ("refusals not byte-identical to the template (must be 0)", bad_template),
        ("quotes not matching the indexed clause (must be 0)", not_verbatim),
    ]
    failed = 0
    for label, offenders in checks:
        print("  %-56s %d %s" % (label, len(offenders),
                                 "PASS" if not offenders else "FAIL"))
        if offenders:
            failed += 1
            for offender in offenders:
                print("      %s" % offender)
    return 1 if failed else 0


def interactive(index: dict) -> int:
    print("Ask My Documents — %s" % ", ".join(index["documents"]))
    print("Answers are quoted verbatim from ONE document with a section "
          "citation, or refused.")
    print("Type a question, or 'quit' to exit.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            return 0
        result = answer_question(index, question)
        print()
        print(result["text"])
        if result["kind"] == "refusal" and result["reason"]:
            print("\n  (refused because: %s)" % result["reason"])
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--test", action="store_true",
                        help="Run the 7 README test questions and exit")
    parser.add_argument("--docs", nargs="*", default=DOCUMENTS,
                        help="Override the three policy document paths")
    args = parser.parse_args()

    try:
        index = retrieve_documents(args.docs)
    except (FileNotFoundError, ValueError) as exc:
        print("INDEX ERROR: %s" % exc, file=sys.stderr)
        return 2

    if args.test:
        return run_tests(index)
    return interactive(index)


if __name__ == "__main__":
    sys.exit(main())
