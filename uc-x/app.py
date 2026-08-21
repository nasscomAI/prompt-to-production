"""
UC-X — Ask My Documents

Answers policy questions from three documents, using exactly one of them per
answer.

The single-source rule is enforced by the shape of the pipeline rather than by
a check bolted on at the end. Retrieval picks a winning *document* first; only
sections belonging to that document are then eligible to be quoted. There is no
code path in which passages from two files can reach the same answer, so the
final assertion that every response cites one filename is a backstop, not the
mechanism.

That ordering matters. A system that gathers the best passages first and filters
for consistency afterwards has already built the blended answer — it is only
hoping to catch it.

Run:
    python app.py                 # interactive
    python app.py --test          # the 7 canonical test questions
    python app.py --question "Can I carry forward unused annual leave?"
"""
import argparse
import math
import os
import re
import sys

DOC_DIR = os.path.join("..", "data", "policy-documents")
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# --- Enforcement rule 3: the refusal template ---------------------------------
# A constant, never a format string assembled per question, so it cannot drift.
#
# [relevant team] is left unfilled deliberately. Naming the owning team requires
# knowing which department owns the topic — and a refusal fires precisely when
# the documents are silent about that topic. Guessing the team would be the same
# hallucination the template exists to prevent, committed inside the sentence
# designed to prevent it.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# --- Enforcement rule 2: hedging is banned ------------------------------------
# Checked against every emitted answer. Hedging is how a system says "I am
# guessing" while sounding authoritative; a system with a refusal template
# never needs it.
HEDGING_PHRASES = [
    "while not explicitly covered",
    "not explicitly",
    "typically",
    "generally understood",
    "generally speaking",
    "it is common practice",
    "usually",
    "in most cases",
    "it is likely",
    "should be fine",
    "presumably",
    "as a general rule",
]

STOPWORDS = {
    "the", "and", "for", "are", "can", "cant", "does", "did", "you", "your", "our", "their",
    "with", "from", "that", "this", "there", "what", "when", "where", "which", "who", "whom",
    "how", "why", "have", "has", "had", "was", "were", "will", "would", "should", "could",
    "any", "all", "some", "not", "but", "its", "his", "her", "them", "they", "she", "him",
    "use", "using", "used", "get", "getting", "want", "need", "please", "tell", "about",
    "into", "onto", "than", "then", "also", "just", "like", "make", "made", "take", "same",
    "day", "days", "one", "two", "may", "might", "must", "able", "allowed", "let",
}

# Refusal thresholds — deliberately conservative. See agents.md.
MIN_DISTINCT_TERMS = 2
MIN_COVERAGE = 1 / 3
# When the second-best document scores within 20% of the best, the question is
# not cleanly owned by any one document and the agent refuses. This threshold is
# what catches the personal-phone question: the finance policy scores 8.24, the
# IT policy 6.90 (a ratio of 0.84), because all three documents talk about
# phones, work and home. Answering from the higher score would have cited the
# finance policy's internet-reimbursement clause at a question about device
# access — a confident citation to a section that does not answer the question.
AMBIGUITY_RATIO = 0.80
# A cited clause never travels alone: the rest of its numbered group comes with
# it, so a limit or a second approver in a neighbouring clause cannot be read
# out of context. Capped to keep an answer readable.
MAX_GROUP_CITATIONS = 8

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
BANNER = re.compile(r"^[═=─-]{5,}\s*$")


def retrieve_documents(paths) -> list:
    """
    Load every policy file and index each numbered section, tagged with the
    filename it came from.

    Provenance is attached here, at read time. A passage separated from its
    filename cannot be checked for single-source compliance, so the two never
    travel apart.
    """
    index = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except OSError as exc:
            sys.exit("Cannot read policy document %s: %s" % (path, exc))

        document = os.path.basename(path)
        heading = ""
        current = None
        found = 0

        for line in lines:
            if BANNER.match(line):
                continue
            stripped = line.strip()
            section_match = SECTION_RE.match(stripped)
            heading_match = HEADING_RE.match(stripped)

            if section_match:
                current = {
                    "document": document,
                    "section": section_match.group(1),
                    "heading": heading,
                    "text": section_match.group(2),
                }
                index.append(current)
                found += 1
            elif heading_match:
                heading = heading_match.group(2).strip()
                current = None
            elif stripped and current is not None:
                current["text"] += " " + stripped

        if not found:
            sys.exit("Parse failure: %s yielded no numbered sections." % path)

    for record in index:
        record["text"] = re.sub(r"\s+", " ", record["text"]).strip()
    return index


def build_stats(index: list) -> dict:
    """
    Count, for every stem, how many sections contain it.

    This is what separates evidence from noise. "work" occurs across all three
    documents and says almost nothing about which one answers a question;
    "install" occurs in two sections of one document and says almost
    everything. Scoring them equally is why the first version refused the Slack
    question as ambiguous and answered the personal-phone question from the
    finance policy — the common words drowned the discriminating ones.
    """
    document_frequency = {}
    for record in index:
        blob = (record["text"] + " " + record["heading"]).lower()
        stems = {_stem(w) for w in re.findall(r"[a-z][a-z\-]*", blob) if len(w) >= 3}
        for stem in stems:
            document_frequency[stem] = document_frequency.get(stem, 0) + 1
    return {"n": len(index), "df": document_frequency}


def _terms(question: str):
    """Content words of the question, stemmed to a shared prefix."""
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]*", question.lower())
    return [w for w in words if len(w) >= 3 and w not in STOPWORDS]


def _stem(term: str) -> str:
    """
    Crude but predictable: the first five characters carry the shared root.
    "approves", "approval" and "approved" all reduce to "appro", which is what
    lets "Who approves leave without pay?" find "requires approval from".
    """
    return term[:5] if len(term) >= 6 else term


def _idf(stem: str, stats: dict) -> float:
    """Rare terms carry the evidence. Smoothed so it is always positive."""
    return math.log((stats["n"] + 1) / (stats["df"].get(stem, 0) + 1)) + 1.0


def _score_section(record: dict, terms, stats: dict) -> tuple:
    """Return (score, matched_terms) for one section against the question."""
    body = record["text"]
    heading = record["heading"]
    matched = set()
    score = 0.0
    for term in set(terms):
        stem = _stem(term)
        pattern = r"\b" + re.escape(stem) + r"\w*"
        body_hits = len(re.findall(pattern, body, flags=re.IGNORECASE))
        heading_hits = len(re.findall(pattern, heading, flags=re.IGNORECASE))
        if not body_hits and not heading_hits:
            continue
        matched.add(term)
        # A heading match is context, not content — it should never carry the
        # same weight as the section actually saying the thing.
        weight = 1.0 if body_hits else 0.4
        hits = body_hits or heading_hits
        score += _idf(stem, stats) * weight * (1 + min(hits - 1, 3) * 0.1)
    return score, matched


def _refusal(reason: str) -> dict:
    return {
        "kind": "REFUSAL",
        "document": "",
        "citations": [],
        "body": REFUSAL_TEMPLATE,
        "reason": reason,
    }


def answer_question(question: str, index: list, stats: dict = None) -> dict:
    """
    Return a single-source cited answer, or the refusal template.

    The document is chosen before any passage is selected, which is what makes
    blending structurally impossible rather than merely discouraged.
    """
    if not question or not question.strip():
        return _refusal("EMPTY_QUESTION")

    if stats is None:
        stats = build_stats(index)

    terms = _terms(question)
    if not terms:
        return _refusal("NO_MATCH")

    scored = []
    for record in index:
        score, matched = _score_section(record, terms, stats)
        if score > 0:
            scored.append((score, matched, record))
    if not scored:
        return _refusal("NO_MATCH")

    # Step 1 — pick the winning DOCUMENT, on its single best section.
    best_by_document = {}
    for score, matched, record in scored:
        current = best_by_document.get(record["document"])
        if current is None or score > current[0]:
            best_by_document[record["document"]] = (score, matched, record)

    ranked_documents = sorted(best_by_document.items(), key=lambda kv: -kv[1][0])
    winner, (top_score, top_matched, _top_record) = ranked_documents[0]

    # Refusal: one incidental word in common is not evidence.
    if len(top_matched) < MIN_DISTINCT_TERMS or len(top_matched) / len(set(terms)) < MIN_COVERAGE:
        return _refusal("NO_MATCH")

    # Refusal: the question sits in the gap between two policies. Picking the
    # higher score by a hair would hide a real ambiguity behind a citation.
    if len(ranked_documents) > 1:
        runner_up_score = ranked_documents[1][1][0]
        if runner_up_score >= top_score * AMBIGUITY_RATIO:
            return _refusal("CROSS_DOCUMENT_AMBIGUITY")

    # Step 2 — only now select passages, and only from the winning document.
    eligible = [
        (score, record) for score, _matched, record in scored if record["document"] == winner
    ]
    eligible.sort(key=lambda pair: (-pair[0], pair[1]["section"]))
    primary = eligible[0][1]

    # A policy answer is a clause group, not a sentence. The question's wording
    # often sits in one clause while the answer sits in its neighbour — "Who
    # approves leave without pay?" matches the words in 5.1 and is answered by
    # 5.2. Returning the whole numbered group keeps the answering clause in
    # view and carries the surrounding conditions with it.
    group = primary["section"].split(".")[0]
    citations = [
        {
            "section": r["section"],
            "heading": r["heading"],
            "text": r["text"],
            "primary": r["section"] == primary["section"],
        }
        for r in index
        if r["document"] == winner and r["section"].split(".")[0] == group
    ]
    citations.sort(key=lambda c: [int(p) for p in c["section"].split(".")])
    citations = citations[:MAX_GROUP_CITATIONS]

    body_lines = [
        "Source: %s — section %s: %s (single document)"
        % (winner, group, primary["heading"]),
        "",
        "Best match: section %s. The rest of section %s is included so that no"
        % (primary["section"], group),
        "condition is read in isolation from the clause it qualifies.",
    ]
    for citation in citations:
        body_lines.append("")
        marker = "->" if citation["primary"] else "  "
        body_lines.append("  %s section %s" % (marker, citation["section"]))
        body_lines.append('       "%s"' % citation["text"])
    body = "\n".join(body_lines)

    response = {
        "kind": "ANSWER",
        "document": winner,
        "citations": citations,
        "body": body,
        "reason": "",
    }

    # Backstop assertions. The pipeline above should make both impossible; if
    # either fires, the response is downgraded to a refusal rather than printed.
    if len({c["section"] for c in citations}) == 0:
        return _refusal("NO_MATCH")
    lowered = body.lower()
    if any(phrase in lowered for phrase in HEDGING_PHRASES):
        return _refusal("NO_MATCH")
    return response


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def render(question: str, response: dict) -> str:
    lines = ["Q: %s" % question, ""]
    if response["kind"] == "REFUSAL":
        lines.append(response["body"])
        lines.append("")
        lines.append("[refusal reason: %s]" % response["reason"])
    else:
        lines.append(response["body"])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default=DOC_DIR, help="Directory holding the 3 policy files")
    parser.add_argument("--question", help="Ask one question and exit")
    parser.add_argument("--test", action="store_true", help="Run the 7 canonical test questions")
    args = parser.parse_args()

    paths = [os.path.join(args.docs, name) for name in DOCUMENTS]
    index = retrieve_documents(paths)

    if args.test:
        for question in TEST_QUESTIONS:
            print("=" * 72)
            print(render(question, answer_question(question, index)))
        print("=" * 72)
        return

    if args.question:
        print(render(args.question, answer_question(args.question, index)))
        return

    print("Ask My Documents — %d sections indexed from %d documents." % (len(index), len(paths)))
    print("Every answer comes from one document only. Blank line or Ctrl-C to quit.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            return
        print()
        print(render(question, answer_question(question, index)))
        print()


if __name__ == "__main__":
    main()
