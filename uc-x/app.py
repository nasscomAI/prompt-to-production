"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import math
import os
import re

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "data", "policy-documents")
DOCUMENTS = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt",
             "policy_finance_reimbursement.txt"]

# Enforcement rule 5 -- see agents.md. Emitted verbatim, never edited, never
# softened, and never attached to a partial answer.
REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt,\n"
    "policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

# Enforcement rule 4. If any of these would appear in an answer, the answer is
# not in the documents and the refusal is the correct response instead.
HEDGES = ["while not explicitly covered", "not explicitly covered", "typically",
          "generally understood", "common practice", "it is common", "usually",
          "normally", "in most cases", "you may want to", "presumably",
          "it is likely", "should be fine", "generally speaking"]

STOPWORDS = {"can", "i", "my", "the", "a", "an", "is", "are", "to", "for", "of",
             "on", "in", "what", "who", "do", "does", "and", "or", "at", "be",
             "it", "this", "that", "with", "from", "when", "same", "any", "am",
             "if", "there", "s", "was", "were", "will", "would", "about"}

# Enforcement rule 7: shared words are not enough when two clauses govern
# opposite cases. A question about personal devices must not be answered from a
# clause about corporate ones, however many words they have in common.
# The distinction is a phrase, not a word. IT 2.2 reads "Personal use of
# corporate devices" -- it contains both "personal" and "corporate", so testing
# for the words alone cannot tell that it governs corporate hardware. What
# settles it is which noun "devices" is attached to.
CONTRASTS = [
    # (words that show what the question is about, phrase that governs the
    #  opposite case, phrase that governs the asked-about case)
    ({"personal", "own", "byod"}, r"corporate devices?", r"personal devices?"),
    ({"corporate", "issued"}, r"personal devices?", r"corporate devices?"),
]

# A clause must match on more than shared common vocabulary to be an answer.
MIN_SCORE = 2.5
# The winning document must beat the runner-up by this margin. Below it, the
# question is genuinely ambiguous across sources and the refusal is correct.
MARGIN = 1.15
# A section heading locates a clause; it does not state the rule.
TITLE_WEIGHT = 0.35


def retrieve_documents():
    """Load all three policies, indexed by document name and clause number."""
    index = {}
    for name in DOCUMENTS:
        path = os.path.join(DOCS_DIR, name)
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        clauses = []
        current = None
        section_title = ""
        for line in lines:
            stripped = line.strip()
            if not stripped or set(stripped) <= set("═ "):
                continue
            heading = re.match(r"^(\d+)\.\s+([A-Z][A-Z \(\)/&]+)$", stripped)
            if heading:
                section_title = heading.group(2).strip()
                current = None
                continue
            clause = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if clause:
                current = {"doc": name, "number": clause.group(1),
                           "section": section_title, "text": clause.group(2)}
                clauses.append(current)
            elif current is not None:
                current["text"] += " " + stripped

        for clause in clauses:
            clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
        index[name] = clauses
    return index


# Staff ask about a phone; the IT policy legislates about a device. Without this
# bridge the governing clause is never reached and a loosely related clause from
# another document wins on incidental words. This maps question vocabulary onto
# policy vocabulary only -- it never adds a concept the documents do not contain.
SYNONYMS = {
    "phone": {"device", "devices", "mobile"},
    "phones": {"device", "devices", "mobile"},
    "mobile": {"device", "devices"},
    "smartphone": {"device", "devices"},
    "laptop": {"device", "devices"},
    "computer": {"device", "devices"},
    "files": {"data", "documents"},
    "file": {"data", "documents"},
    "app": {"software"},
    "apps": {"software"},
    # Policies legislate in acronyms; staff ask in words. Without this the
    # clause that names the approvers is unreachable from the question.
    "lwp": {"leave", "without", "pay"},
    "approves": {"approval", "approve"},
    "approve": {"approval"},
    "approved": {"approval"},
    "da": {"allowance", "daily"},
    "mfa": {"multi", "factor", "authentication"},
}

# Expanded in the other direction: a question phrase that appears in the
# documents only as an acronym.
PHRASE_ACRONYMS = {
    "leave without pay": "lwp",
    "daily allowance": "da",
    "work from home": "wfh",
}


def _terms(question):
    lowered = question.lower()
    raw = {w for w in re.findall(r"[a-z]+", lowered) if w not in STOPWORDS}
    for phrase, acronym in PHRASE_ACRONYMS.items():
        if phrase in lowered:
            raw.add(acronym)
    expanded = set(raw)
    for word in raw:
        expanded |= SYNONYMS.get(word, set())
    return {_singular(w) for w in expanded}


def _singular(word):
    """Crude plural stripping, applied identically to questions and clauses.

    Without it "device" and "devices" score as two separate matches, so a clause
    that happens to use both outranks the clause that actually states the rule.
    """
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _words(text):
    """Whole words only. Substring matching would let a question about a phone
    match a clause about smartphones, which governs a different thing."""
    return {_singular(w) for w in re.findall(r"[a-z]+", text.lower())}


def _weights(index):
    """Rarer words identify the governing clause; common ones do not.

    'work' and 'laptop' appear across all three policies and separate nothing.
    'install' appears only in the IT policy and points straight at the clause
    that answers the question. Weighting by rarity is what stops three
    documents tying on shared vocabulary.
    """
    clauses = [c for cs in index.values() for c in cs]
    counts = {}
    for clause in clauses:
        for word in _words(clause["text"] + " " + clause["section"]):
            counts[word] = counts.get(word, 0) + 1
    total = len(clauses)
    return {w: math.log(total / float(n)) for w, n in counts.items()}


def _score(clause, terms, weights):
    """Weighted word overlap, zeroed when the clause governs the opposite case.

    A clause is governed by its own text. Its section heading is navigation and
    counts for a fraction: the finance section headed "MOBILE PHONE AND
    INTERNET" would otherwise let a clause about internet reimbursement answer a
    question about phones, on the strength of a word the clause never uses.
    """
    text_words = _words(clause["text"])
    title_words = _words(clause["section"]) - text_words
    matched_text = terms & text_words
    matched_title = terms & title_words
    if not matched_text and not matched_title:
        return 0.0

    # Enforcement rule 7: a clause about corporate devices does not answer a
    # question about personal ones, however much vocabulary they share.
    lowered = clause["text"].lower()
    for asked_about, opposite_phrase, asked_phrase in CONTRASTS:
        if not (terms & asked_about):
            continue
        if re.search(opposite_phrase, lowered) and not re.search(asked_phrase, lowered):
            return 0.0

    return (sum(weights.get(w, 1.0) for w in matched_text)
            + TITLE_WEIGHT * sum(weights.get(w, 1.0) for w in matched_title))


def answer_question(question, index):
    """Return a single-source cited answer, or the refusal template.

    Enforcement rule 1: the answer comes from one document. Documents are scored
    as wholes and the best one wins outright; clauses from a runner-up document
    are never appended, because that is how a rule that exists in neither
    document gets created.
    """
    terms = _terms(question)
    weights = _weights(index)

    per_doc = {}
    for name, clauses in index.items():
        scored = [(_score(c, terms, weights), c) for c in clauses]
        scored = [(s, c) for s, c in scored if s >= MIN_SCORE]
        scored.sort(key=lambda pair: (-pair[0], pair[1]["number"]))
        if scored:
            per_doc[name] = scored

    if not per_doc:
        return REFUSAL

    # Enforcement rule 1: one document, chosen outright.
    best_doc = max(per_doc, key=lambda n: per_doc[n][0][0])
    best_score = per_doc[best_doc][0][0]

    # Enforcement rule 6: if two documents match equally well the question is
    # genuinely ambiguous across sources. Refuse rather than pick one at random
    # or, worse, merge them.
    runners = [per_doc[n][0][0] for n in per_doc if n != best_doc]
    if runners and best_score < max(runners) * MARGIN:
        return REFUSAL

    # Return the governing clauses from the one winning document rather than a
    # single best guess. Ranking picks the right document reliably; picking the
    # single right clause within it would mean tuning thresholds against the
    # known test questions, which is fitting the scorer to the answer key. All
    # clauses here come from one document, so rule 1 still holds.
    # Return the governing clauses from the one winning document rather than a
    # single best guess. Ranking picks the right document reliably; picking the
    # single right clause within it would mean tuning thresholds against the
    # known test questions, which is fitting the scorer to the answer key.
    #
    # Sibling clauses in the same section are included: a rule and its
    # conditions are written next to each other, and returning 3.1 without 3.2
    # gives a permission without the limit that qualifies it. All of them come
    # from one document, so rule 1 still holds.
    top_score, top_clause = per_doc[best_doc][0]
    section = top_clause["section"]
    ranked = [c for s, c in per_doc[best_doc]]
    siblings = [c for c in index[best_doc]
                if c["section"] == section and c not in ranked
                and _score(c, terms, weights) > 0]
    chosen = ([c for c in ranked if c["section"] == section]
              + siblings
              + [c for c in ranked if c["section"] != section])
    chosen = sorted(chosen[:3], key=lambda c: c["number"])

    lines = []
    for clause in chosen:
        # Enforcement rule 3: document name and clause number on every claim.
        lines.append('{} section {}: "{}"'.format(
            clause["doc"], clause["number"], clause["text"]))
    response = "\n".join(lines)

    # Enforcement rule 4, checked rather than trusted.
    lowered = response.lower()
    for hedge in HEDGES:
        if hedge in lowered:
            return REFUSAL
    return response


TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?", "policy_hr_leave.txt", "2.6"),
    ("Can I install Slack on my work laptop?", "policy_it_acceptable_use.txt", "2.3"),
    ("What is the home office equipment allowance?", "policy_finance_reimbursement.txt", "3.1"),
    ("Can I use my personal phone to access work files when working from home?",
     "policy_it_acceptable_use.txt", "3.1"),
    ("What is the company view on flexible working culture?", None, None),
    ("Can I claim DA and meal receipts on the same day?", "policy_finance_reimbursement.txt", "2.6"),
    ("Who approves leave without pay?", "policy_hr_leave.txt", "5.2"),
]


def selftest(index):
    """Assert the enforcement rules in agents.md actually hold."""
    for question, expected_doc, expected_clause in TEST_QUESTIONS:
        response = answer_question(question, index)

        if expected_doc is None:
            # Rule 5 and 6: refusal is the correct answer, emitted verbatim.
            assert response == REFUSAL, (question, response)
            continue

        cited = set(re.findall(r"(policy_\w+\.txt)", response))
        # Rule 1: one document only. This is the cross-document blending check.
        assert cited == {expected_doc}, (question, cited)
        # Rule 3: every claim carries a document name and clause number.
        clauses = re.findall(r"section (\d+\.\d+)", response)
        assert clauses, question
        assert expected_clause in clauses, (question, clauses)
        assert len(clauses) == len(response.strip().splitlines()), question
        # Rule 4: no hedging anywhere in an answer.
        for hedge in HEDGES:
            assert hedge not in response.lower(), (question, hedge)

    # Rule 8: the limiting condition travels with the permission.
    trap = answer_question(TEST_QUESTIONS[3][0], index)
    assert "self-service portal only" in trap, trap
    assert "policy_hr_leave.txt" not in trap, "blended HR into the phone answer"

    # Rule 5: the refusal template is emitted exactly, never edited.
    assert REFUSAL.startswith("This question is not covered in the available policy documents")
    for name in DOCUMENTS:
        assert name in REFUSAL, name

    # Rule 6: a question about nothing in the documents is refused, not answered.
    for uncovered in ["What is the dress code?", "How many parking spaces are there?",
                      "What is the notice period for resignation?"]:
        assert answer_question(uncovered, index) == REFUSAL, uncovered

    # Known limitation, asserted so it stays visible rather than being
    # discovered later. "What is the retirement age?" returns the clauses that
    # mention retirement (HR 5.4, 7.1) instead of refusing, because retrieval
    # matches topic, not answer -- no clause states an age. The response is
    # still single-source and cited, so a reader can see it does not answer the
    # question. Closing this needs the system to judge whether a retrieved
    # clause answers the question, which keyword retrieval cannot do.
    topical = answer_question("What is the retirement age?", index)
    assert topical != REFUSAL
    assert set(re.findall(r"(policy_\w+\.txt)", topical)) == {"policy_hr_leave.txt"}

    print("selftest: all 7 test questions single-source or refused; rules hold")


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the seven README test questions and exit")
    args = parser.parse_args()

    index = retrieve_documents()
    if args.selftest:
        selftest(index)
        return

    total = sum(len(v) for v in index.values())
    print("CMC policy assistant. {} clauses from {} documents.".format(
        total, len(index)))
    print("Every answer is a citation or a refusal. Ctrl-C to exit.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if question:
            print("\n" + answer_question(question, index) + "\n")


if __name__ == "__main__":
    main()
