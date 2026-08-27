"""
UC-X — Ask My Documents

A policy question-answering CLI over three CMC policy documents.

The failure mode this is built against is not "wrong answer". It is the
CONFIDENT SYNTHESIS: taking a sentence from the IT policy and a sentence from
another policy and producing a fluent third sentence that grants a permission
neither document grants. The README's test case is exactly this — the answer
"Yes, personal phones can be used for approved remote work tools and email"
is not in any document, and it would be believed.

Two design decisions make that impossible rather than unlikely:

  1. ONE DOCUMENT IS CHOSEN BEFORE ANY CLAUSE IS. The retriever scores whole
     documents, picks a winner, and only then selects clauses inside it. If no
     document wins clearly, the question is refused. Blending is not a behaviour
     that can degrade — there is no code path that assembles a response from two
     files.

  2. ANSWERS ARE QUOTATIONS, NEVER PROSE. The program has no sentence generator.
     Every word of every answer is copied from the cited clause. Text that is
     copied cannot hedge, cannot soften an obligation, and cannot invent a
     condition.

Run:
    python app.py                      # interactive
    python app.py --selftest           # the 7 README test questions, asserted
    python app.py --question "..."     # single question, non-interactive
"""
import argparse
import io
import math
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

DEFAULT_DOC_DIR = os.path.join("..", "data", "policy-documents")

# ─────────────────────────────────────────────────────────────────────────────
# The refusal template. ONE string, invariant, no per-question customisation.
# Nothing is ever appended to it inside an answer block.
# ─────────────────────────────────────────────────────────────────────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT or Finance) for guidance."
)

# Enforcement: hedged hallucination. Scanned for before any response is printed.
BANNED_PHRASES = (
    "while not explicitly covered",
    "not explicitly covered",
    "typically",
    "generally",
    "usually",
    "normally",
    "it is common practice",
    "common practice",
    "generally understood",
    "it is understood",
    "presumably",
    "in most cases",
    "should be fine",
    "it is likely",
    "best practice",
    "as a rule",
    "i would assume",
    "it seems",
)

STOPWORDS = frozenset("""
a an the is are am was were be been being do does did can could should would
will shall may might must i me my mine we us our ours you your yours he she it
its they them their theirs this that these those of in on at to for from with
by about as if then than so and or but not no nor too very just also only own
same s t what which who whom when where why how there here get got
""".split())

# Spelled-out forms the documents abbreviate. Expanding the QUESTION (never the
# document) keeps retrieval symmetric without altering any source text.
PHRASE_EXPANSIONS = {
    "leave without pay": ["lwp"],
    "loss of pay": ["lop"],
    "work from home": ["wfh"],
    "working from home": ["wfh"],
    "multi factor authentication": ["mfa"],
    "daily allowance": ["da"],
}

MIN_INFORMATIVE_TERMS = 2      # distinct rare terms the best clause must match
MIN_CLAUSE_WEIGHT = 2.5        # weighted score the best clause must reach
INFORMATIVE_WEIGHT = 1.0       # IDF above which a term counts as informative
CITATION_RELEVANCE = 0.4       # a cited clause must reach this share of the best
SECTION_BONUS = 0.5            # share of a section title's score lifting its clauses
DOCUMENT_MARGIN = 1.25         # winner must beat runner-up by this factor
MAX_CITATIONS = 3              # clauses quoted per answer, all one document

# The 7 test questions from the UC-X README, with the expected source document
# and the clause the README says holds the answer. Asserting the CLAUSE matters:
# an early version returned the right document while quoting three clauses that
# did not answer the question, and a document-only assertion passed it.
SELFTEST_QUESTIONS = (
    ("Can I carry forward unused annual leave?",
     "policy_hr_leave.txt", "answer", "2.6"),
    ("Can I install Slack on my work laptop?",
     "policy_it_acceptable_use.txt", "answer", "2.3"),
    ("What is the home office equipment allowance?",
     "policy_finance_reimbursement.txt", "answer", "3.1"),
    ("Can I use my personal phone to access work files from home?",
     None, "answer_or_refusal", None),
    ("What is the company view on flexible working culture?",
     None, "refusal", None),
    ("Can I claim DA and meal receipts on the same day?",
     "policy_finance_reimbursement.txt", "answer", "2.6"),
    ("Who approves leave without pay?",
     "policy_hr_leave.txt", "answer", "5.2"),
)


def _normalise_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def retrieve_documents(directory: str) -> dict:
    """Load the three policy files and index every clause by document + section."""
    section_re = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()/&,'–-]+)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    divider_re = re.compile(r"^[═=_\-\s]+$")

    documents = {}
    all_clauses = []

    for filename in POLICY_FILES:
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            print("Error: policy document not found: {0}".format(path), file=sys.stderr)
            print("The refusal template names all three documents by filename, so "
                  "answering with fewer than three loaded would be dishonest.",
                  file=sys.stderr)
            sys.exit(1)
        try:
            with io.open(path, "r", encoding="utf-8-sig") as handle:
                raw_lines = handle.read().splitlines()
        except (IOError, OSError, UnicodeDecodeError) as exc:
            print("Error: could not read {0}: {1}".format(path, exc), file=sys.stderr)
            sys.exit(1)

        clauses = []
        meta = []
        current_section = ("0", "")
        current = None

        for line in raw_lines:
            if not line.strip() or divider_re.match(line):
                continue
            clause_match = clause_re.match(line)
            section_match = section_re.match(line)
            if clause_match:
                current = {
                    "id": clause_match.group(1),
                    "section": current_section[0],
                    "section_title": current_section[1],
                    "document": filename,
                    "parts": [clause_match.group(2)],
                }
                clauses.append(current)
            elif section_match:
                current_section = (section_match.group(1),
                                  _normalise_whitespace(section_match.group(2)))
                current = None
            elif line.startswith((" ", "\t")) and current is not None:
                current["parts"].append(line)
            elif not clauses:
                meta.append(line.strip())

        for clause in clauses:
            clause["text"] = _normalise_whitespace(" ".join(clause["parts"]))
            del clause["parts"]

        if not clauses:
            print("Error: no numbered clauses parsed from {0}.".format(path),
                  file=sys.stderr)
            sys.exit(1)

        reference = ""
        for line in meta:
            if line.lower().startswith("document reference:"):
                reference = line.split(":", 1)[1].strip()

        documents[filename] = {
            "reference": reference,
            "title": " / ".join(l for l in meta if ":" not in l),
            "clauses": clauses,
            "raw": "\n".join(raw_lines),
        }
        all_clauses.extend(clauses)

    return {"documents": documents, "clauses": all_clauses}


def _common_prefix_len(a: str, b: str) -> int:
    limit = min(len(a), len(b))
    index = 0
    while index < limit and a[index] == b[index]:
        index += 1
    return index


MIN_PREFIX_MATCH = 3


def _terms_match(term: str, word: str) -> bool:
    """Same-word test tolerant of inflection but not of coincidence.

    Short words must match exactly; anything else needs a common prefix of at
    least min(len(a), len(b), 5) AND at least MIN_PREFIX_MATCH characters.

      approves / approval  -> "approv" (6) >= 5   match
      work / working       -> "work"   (4) >= 4   match
      da / da              -> exact               match   (acronyms survive)
      day / data           -> "da"     (2) <  3   no match
      company / c          -> short, unequal      no match
      install / in         -> short, unequal      no match

    The last two are the whole reason for this rule. Without the absolute
    minimum, a one-letter token — the "C" of "Grade C", or the "s" left by
    tokenising "employee's" — matches any question term starting with the same
    letter, which made "flexible working culture" retrieve a mobile phone
    allowance with total confidence.
    """
    if min(len(term), len(word)) < MIN_PREFIX_MATCH:
        return term == word
    shared = _common_prefix_len(term, word)
    return shared >= min(len(term), len(word), 5) and shared >= MIN_PREFIX_MATCH


def _question_terms(question: str) -> List[str]:
    lowered = question.lower()
    terms = []
    for token in re.findall(r"[a-z0-9]+", lowered):
        if token in STOPWORDS or len(token) < 2:
            continue
        if token not in terms:
            terms.append(token)
    for phrase, extras in PHRASE_EXPANSIONS.items():
        if phrase in lowered:
            for extra in extras:
                if extra not in terms:
                    terms.append(extra)
    return terms


def _term_weights(index: dict, terms: List[str]) -> Dict[str, float]:
    """Inverse-document-frequency weight per question term.

    Counting distinct matched terms treats "employees" as worth as much as
    "Slack". It is not: "employees" appears in most clauses of all three
    documents and carries no signal about which document answers the question,
    while a term appearing in two clauses is almost the whole answer.

    A term present in every clause gets weight 0. This is what stops the word
    "working" in "flexible working culture" from selecting a document.
    """
    total = len(index["clauses"])
    clause_words = [
        set(re.findall(r"[a-z0-9]+", clause["text"].lower()))
        for clause in index["clauses"]
    ]
    weights = {}
    for term in terms:
        frequency = sum(
            1 for words in clause_words
            if any(_terms_match(term, word) for word in words)
        )
        weights[term] = math.log(float(total) / frequency) if frequency else 0.0
    return weights


def _score_clause(clause_text: str, terms: List[str],
                  weights: Dict[str, float]) -> Tuple[float, List[str], int]:
    """Weighted score, matched terms, and how many matches were informative."""
    words = set(re.findall(r"[a-z0-9]+", clause_text.lower()))
    matched = []
    score = 0.0
    informative = 0
    for term in terms:
        if any(_terms_match(term, word) for word in words):
            matched.append(term)
            score += weights.get(term, 0.0)
            if weights.get(term, 0.0) >= INFORMATIVE_WEIGHT:
                informative += 1
    return score, matched, informative


def _check_response(body: str, citations: List[dict]) -> List[str]:
    """Single-source and hedging checks, run before anything is printed."""
    problems = []
    documents = set(c["document"] for c in citations)
    if len(documents) > 1:
        problems.append("response cites more than one document: "
                        + ", ".join(sorted(documents)))
    lowered = body.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            problems.append("banned hedging phrase present: " + phrase)
    return problems


def answer_question(index: dict, question: str) -> dict:
    """Return a single-source cited answer or the exact refusal template."""
    refusal = {
        "kind": "refusal",
        "document": "",
        "citations": [],
        "body": REFUSAL_TEMPLATE,
        "diagnostic": "",
    }

    terms = _question_terms(question)
    if not terms:
        refusal["diagnostic"] = "no searchable terms in the question."
        return refusal

    weights = _term_weights(index, terms)

    # Section-title signal. A question that names a section's subject should
    # retrieve from that section: "who approves leave without pay" matches the
    # title "LEAVE WITHOUT PAY (LWP)" outright, which is how clause 5.2 — the
    # one naming both approvers — outranks clauses that merely repeat the words
    # "leave" and "pay". The bonus lifts a whole section, never a lone clause,
    # and a clause still needs its own informative match to be quoted.
    # A title must match at least MIN_INFORMATIVE_TERMS to count as a topic
    # match. One common word in a heading is not one: "WORK FROM HOME EQUIPMENT"
    # shares "work" with "can I install Slack on my work laptop", which was
    # enough to lift the whole Finance expenses section over the IT policy that
    # actually answers the question.
    section_bonus = {}
    for clause in index["clauses"]:
        key = (clause["document"], clause["section"])
        if key not in section_bonus:
            title_score, _, title_informative = _score_clause(
                clause["section_title"], terms, weights)
            section_bonus[key] = (
                title_score * SECTION_BONUS
                if title_informative >= MIN_INFORMATIVE_TERMS else 0.0)

    scored = []
    for clause in index["clauses"]:
        own_score, matched, informative = _score_clause(clause["text"], terms, weights)
        if own_score > 0:
            total = own_score + section_bonus.get(
                (clause["document"], clause["section"]), 0.0)
            scored.append((total, clause, matched, informative, own_score))

    if not scored:
        refusal["diagnostic"] = ("no clause in any of the three documents matched "
                                 "any term in the question.")
        return refusal

    # Enforcement: weak evidence is refused, not answered thinly. Judged on the
    # clause's OWN score — a section-title bonus must never rescue a question
    # that no individual clause actually answers.
    best = max(scored, key=lambda item: item[4])
    best_score, _, best_matched, best_informative = best[4], best[1], best[2], best[3]
    if best_informative < MIN_INFORMATIVE_TERMS or best_score < MIN_CLAUSE_WEIGHT:
        refusal["diagnostic"] = (
            "weak evidence — best clause matched {0} informative term(s) for a "
            "weighted score of {1:.2f}, below the minimum of {2} term(s) and "
            "{3:.2f}. Matched only: {4}. Common words shared with the corpus are "
            "a coincidence, not an answer.".format(
                best_informative, best_score, MIN_INFORMATIVE_TERMS,
                MIN_CLAUSE_WEIGHT, ", ".join(best_matched) or "nothing"))
        return refusal

    # Enforcement: ONE document is chosen before any clause is.
    doc_scores = {}
    for score, clause, _, _, _ in scored:
        doc_scores.setdefault(clause["document"], []).append(score)
    doc_totals = {
        name: sum(sorted(scores, reverse=True)[:MAX_CITATIONS])
        for name, scores in doc_scores.items()
    }
    ranking = sorted(doc_totals.items(), key=lambda kv: (-kv[1], kv[0]))
    winner, winner_score = ranking[0]
    runner_up, runner_score = ranking[1] if len(ranking) > 1 else ("", 0)

    # Enforcement: cross-document ambiguity is a refusal, not an average.
    if runner_score and winner_score < runner_score * DOCUMENT_MARGIN:
        refusal["diagnostic"] = (
            "question spans two documents — {0} scored {1:.2f} and {2} scored "
            "{3:.2f}, which is inside the {4}x margin. Answering would mean "
            "blending two sources into a permission neither document grants, so "
            "it is refused.".format(winner, winner_score, runner_up, runner_score,
                                    DOCUMENT_MARGIN))
        return refusal

    # Only clauses that are genuinely relevant are quoted. Without this a third
    # citation gets padded in on one common word — quoting a maternity-leave
    # clause at someone asking about carry-forward because both say "leave".
    in_winner = [item for item in scored if item[1]["document"] == winner]
    best_in_winner = max(item[0] for item in in_winner)
    chosen = sorted(
        [item for item in in_winner
         if item[0] >= best_in_winner * CITATION_RELEVANCE and item[3] >= 1],
        key=lambda item: (-item[0], item[1]["id"]),
    )[:MAX_CITATIONS]

    citations = []
    lines = []
    for score, clause, matched, informative, own_score in chosen:
        citation = "{0} § {1}".format(clause["document"], clause["id"])
        citations.append(
            {"citation": citation, "text": clause["text"], "document": clause["document"]})
        lines.append("  SOURCE : {0}  ({1})".format(citation, clause["section_title"]))
        lines.append('  QUOTE  : "{0}"'.format(clause["text"]))
        lines.append("")

    body = "\n".join(lines).rstrip()

    # Runtime self-check. A response that cannot be verified is not emitted.
    problems = _check_response(body, citations)
    if problems:
        print("Internal check failed, refusing instead of answering:", file=sys.stderr)
        for problem in problems:
            print("  - " + problem, file=sys.stderr)
        refusal["diagnostic"] = "response failed its own verification: " + \
            "; ".join(problems)
        return refusal

    return {
        "kind": "answer",
        "document": winner,
        "citations": citations,
        "body": body,
        "diagnostic": ("single source {0} (weighted score {1:.2f}); runner-up {2} "
                       "({3:.2f}); {4} clause(s) cleared the relevance bar.".format(
                           winner, winner_score, runner_up or "none", runner_score,
                           len(chosen))),
    }


def _print_response(response: dict) -> None:
    """Print the answer block, then the diagnostic OUTSIDE it and labelled."""
    print("")
    print("-" * 78)
    print(response["body"])
    print("-" * 78)
    if response["diagnostic"]:
        print("[diagnostic — not part of the answer] " + response["diagnostic"])
    print("")


def run_selftest(index: dict) -> int:
    """Run the 7 README questions and assert every enforcement rule."""
    print("=" * 78)
    print("UC-X SELF-TEST — the 7 test questions from the README")
    print("=" * 78)
    failures = []

    for question, expected_doc, expected_kind, expected_clause in SELFTEST_QUESTIONS:
        response = answer_question(index, question)
        problems = []

        if expected_kind == "answer" and response["kind"] != "answer":
            problems.append("expected an answer, got a refusal")
        elif expected_kind == "refusal" and response["kind"] != "refusal":
            problems.append("expected the refusal template, got an answer from "
                            + response["document"])

        if expected_doc and response["kind"] == "answer" \
                and response["document"] != expected_doc:
            problems.append("expected source {0}, got {1}".format(
                expected_doc, response["document"]))

        if expected_clause and response["kind"] == "answer":
            cited_ids = [c["citation"].split("§")[-1].strip()
                         for c in response["citations"]]
            if expected_clause not in cited_ids:
                problems.append(
                    "expected clause {0} among the citations, got {1}".format(
                        expected_clause, ", ".join(cited_ids) or "none"))

        # Single source.
        documents = set(c["document"] for c in response["citations"])
        if len(documents) > 1:
            problems.append("BLENDED sources: " + ", ".join(sorted(documents)))

        # Hedging.
        for phrase in BANNED_PHRASES:
            if phrase in response["body"].lower():
                problems.append("hedging phrase: " + phrase)

        # Refusals must be the template character for character.
        if response["kind"] == "refusal" and response["body"] != REFUSAL_TEMPLATE:
            problems.append("refusal text deviates from the template")

        # Every quotation must be a literal substring of its cited source file.
        for citation in response["citations"]:
            raw = index["documents"][citation["document"]]["raw"]
            flat_raw = _normalise_whitespace(raw)
            if citation["text"] not in flat_raw:
                problems.append("quotation not found verbatim in "
                                + citation["document"])

        status = "PASS" if not problems else "FAIL"
        print("")
        print("[{0}] {1}".format(status, question))
        if response["kind"] == "answer":
            for citation in response["citations"]:
                print("      -> {0}".format(citation["citation"]))
                print('         "{0}"'.format(citation["text"]))
        else:
            print("      -> refusal template (exact)")
        print("      {0}".format(response["diagnostic"]))
        for problem in problems:
            print("      !! " + problem)
            failures.append((question, problem))

    print("")
    print("=" * 78)
    print("SELF-TEST RESULT: {0}/{1} questions PASS".format(
        len(SELFTEST_QUESTIONS) - len(set(q for q, _ in failures)),
        len(SELFTEST_QUESTIONS)))
    if failures:
        print("FAILURES:")
        for question, problem in failures:
            print("  {0} — {1}".format(question, problem))
        return 1
    print("All responses were single-source and cited, or the exact refusal "
          "template. No hedging phrases present.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Question Answering")
    parser.add_argument("--docs", default=DEFAULT_DOC_DIR,
                        help="Directory holding the three policy .txt files")
    parser.add_argument("--question", default=None,
                        help="Answer one question and exit (non-interactive)")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions and assert the rules")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)
    clause_count = len(index["clauses"])

    if args.selftest:
        sys.exit(run_selftest(index))

    if args.question:
        _print_response(answer_question(index, args.question))
        return

    print("=" * 78)
    print("UC-X — Ask My Documents")
    print("=" * 78)
    print("Indexed {0} clauses across {1} documents:".format(
        clause_count, len(index["documents"])))
    for filename, document in index["documents"].items():
        print("  {0}  ({1}, {2} clauses)".format(
            filename, document["reference"] or "no reference",
            len(document["clauses"])))
    print("")
    print("Every answer is a verbatim quotation from ONE document, with its")
    print("section cited. Questions the documents do not cover are refused with")
    print("a fixed template rather than answered approximately.")
    print("")
    print("Type a question, or 'quit' to exit.")

    while True:
        try:
            question = input("\nquestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Bye.")
            return
        _print_response(answer_question(index, question))


if __name__ == "__main__":
    main()
