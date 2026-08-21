"""
UC-X app.py — Ask My Documents
Single-source, cited Q&A over the CMC policy documents. Built via the RICE +
agents.md + skills.md + CRAFT workflow. See README.md for run command and
the 7 test questions.

Enforcement (mirrors agents.md):
  1. Never combines claims from two different documents — answers are built
     from exactly ONE section of ONE document (architecturally enforced).
  2. Never uses hedging phrases.
  3. Questions not covered by the documents get the refusal template EXACTLY.
  4. Every factual answer cites source document name + section number.
"""
import argparse
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "as is standard practice", "generally expected",
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am",
    "can", "could", "may", "might", "will", "would", "shall", "should", "must", "do", "does",
    "did", "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "its", "they",
    "them", "their", "this", "that", "these", "those", "there", "here",
    "to", "of", "in", "on", "at", "for", "with", "from", "by", "about", "into", "over",
    "and", "or", "but", "if", "when", "while", "what", "which", "who", "whom", "whose",
    "how", "why", "where", "any", "some", "please", "tell", "view", "company", "use", "used",
}

# Domain synonym expansion so device/leave questions reach the right sections.
SYNONYMS = {
    "phone": ["device", "mobile"],
    "mobile": ["device", "phone"],
    "smartphone": ["device", "phone"],
    "laptop": ["device", "computer"],
    "computer": ["device", "laptop"],
    "slack": ["software"],
    "install": ["software"],
    "working": ["work"],
    "works": ["work"],
    "claims": ["claim"],
    "claimed": ["claim"],
    "receipts": ["receipt"],
    "approves": ["approval", "approve"],
    "approve": ["approval"],
    "allowance": ["allowance"],
    "encash": ["encashment"],
    "carry": ["carry"],
    "forwarded": ["forward"],
}

TEAM_BY_TOPIC = [
    (re.compile(r"\b(leave|holiday|lwp|lop|maternity|paternity|sick|grievance|hr)\b", re.I), "HR Department"),
    (re.compile(r"\b(device|laptop|phone|software|password|internet|email|wifi|it\b|system)", re.I), "IT Department"),
    (re.compile(r"\b(claim|reimburs|expense|allowance|da\b|travel|hotel|refund)\b", re.I), "Finance Department"),
]

SECTION_HEADER = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-&(),]+)\s*$")
CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")

MIN_BODY_HITS = 2  # concept groups that must appear in a section's BODY

# Questions asking WHO approves / what is required shift weight toward
# sections that actually contain approval/obligation language.
APPROVAL_INTENT = re.compile(r"\b(approv\w*|authoris\w*|authoriz\w*|permission|consent|sign[- ]?off)\b", re.I)
OBLIGATION_MARKERS = re.compile(r"\b(approval|approved|requires|required|permission|permitted|must|consent|not sufficient)\b", re.I)

# Topic routing: when a question clearly belongs to one policy domain, search
# ONLY that document. This structurally forbids cross-document blending.
DOMAIN_ROUTES = [
    (re.compile(r"\b(leave|holidays?|lwp|lop|maternity|paternity|sick)\b", re.I), "policy_hr_leave.txt"),
    (re.compile(r"\b(devices?|laptops?|phones?|software|passwords?|internet|email|wifi|systems?)\b", re.I), "policy_it_acceptable_use.txt"),
    (re.compile(r"\b(claims?|reimburs\w*|expenses?|allowances?|\bda\b|travel|hotel)\b", re.I), "policy_finance_reimbursement.txt"),
]


def route_domain(question):
    """Return the single document a domain-specific question must be answered
    from, or None when the question is not clearly domain-bound."""
    for rx, doc in DOMAIN_ROUTES:
        if rx.search(question):
            return doc
    return None


def parse_policy(text):
    """Parse into list of {id, title, body} preserving wrapped lines."""
    clauses = []
    cur_title = ""
    cur_id, buf = None, []

    def flush():
        if cur_id is not None:
            body = re.sub(r"\s+", " ", " ".join(buf)).strip()
            clauses.append({"id": cur_id, "title": cur_title, "body": body})

    for line in text.splitlines():
        stripped = line.strip()
        if stripped and set(stripped) <= set("═="):
            continue
        m = SECTION_HEADER.match(stripped)
        if m:
            flush()
            cur_id, buf = None, []
            cur_title = "%s. %s" % (m.group(1), m.group(2).strip())
            continue
        m = CLAUSE_START.match(stripped)
        if m:
            flush()
            cur_id = m.group(1)
            buf = [m.group(2)]
            continue
        if cur_id is not None and stripped:
            buf.append(stripped)
    flush()
    return clauses


def load_documents():
    docs = []
    for name in POLICY_FILES:
        path = os.path.join(POLICY_DIR, name)
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                text = f.read()
        except OSError as exc:
            print("ERROR: cannot read policy file '%s': %s" % (path, exc))
            sys.exit(1)
        for c in parse_policy(text):
            c["doc"] = name
            docs.append(c)
    return docs


def token_variants(tok):
    variants = {tok}
    if tok.endswith("ies"):
        variants.add(tok[:-3] + "y")
    if tok.endswith("es"):
        variants.add(tok[:-2])
    if tok.endswith("s"):
        variants.add(tok[:-1])
    if tok.endswith("ing"):
        variants.add(tok[:-3])
        variants.add(tok[:-3] + "e")
    if tok.endswith("ed"):
        variants.add(tok[:-2])
    return variants


def tokenize(question):
    raw = re.findall(r"[a-z0-9]+", question.lower())
    tokens = []
    for t in raw:
        if t in STOPWORDS or len(t) < 2:
            continue
        tokens.append(t)
    return tokens


def _contains_word(text_low, term):
    """Word-boundary prefix match: 'work' hits 'works'/'work-from-home',
    but never mid-word substrings like 'networking'."""
    return re.search(r"\b%s" % re.escape(term), text_low) is not None


def token_group(tok):
    """One concept = the token + its inflections + its synonyms.
    A concept counts AT MOST ONCE per section, so 'phone/mobile/device'
    can never masquerade as three independent pieces of evidence."""
    return frozenset({tok} | set(token_variants(tok)) | set(SYNONYMS.get(tok, [])))


def question_groups(question):
    """Build concept groups from the question, MERGING any groups that share
    a member (so 'work' and 'working' never count as two concepts)."""
    merged = []
    for t in tokenize(question):
        g = set(token_group(t))
        overlap = [m for m in merged if m & g]
        for m in overlap:
            g |= m
            merged.remove(m)
        merged.append(frozenset(g))
    return merged


def group_in(text_low, group):
    return any(_contains_word(text_low, v) for v in group)


def retrieve(docs, question):
    """Score every section; return (best_section, score, distinct_group_hits).

    Concept-group counting, document-frequency weighting and word-boundary
    matching keep generic words like 'work' from manufacturing false matches.
    A section is eligible only if its BODY (not merely its heading) shares at
    least MIN_BODY_HITS concept groups with the question — this prevents
    generic section titles like 'WORK FROM HOME' from capturing questions
    whose real subject lies elsewhere.
    """
    groups = question_groups(question)
    if not groups:
        return None, 0.0, set()

    n_docs = max(len(docs), 1)
    df = {}
    for d in docs:
        text_low = (d["title"] + " " + d["body"]).lower()
        for g in groups:
            if group_in(text_low, g):
                df[g] = df.get(g, 0) + 1

    best, best_score, best_hits = None, 0.0, set()
    for d in docs:
        body_low = d["body"].lower()
        title_low = d["title"].lower()
        body_words = re.findall(r"[a-z0-9]+", body_low)
        hits = set()
        body_hits = set()
        score = 0.0
        member_positions = {}  # group -> word indices where members occur
        for g in groups:
            positions = []
            for v in g:
                for i, w in enumerate(body_words):
                    if w.startswith(v):
                        positions.append(i)
                        break
            in_body = bool(positions)
            in_title = group_in(title_low, g)
            if not (in_body or in_title):
                continue
            hits.add(g)
            if in_body:
                body_hits.add(g)
                member_positions[g] = positions
            w = 3.0 if df.get(g, 0) <= max(2, n_docs // 20) else (2.0 if df.get(g, 0) <= n_docs // 4 else 1.0)
            score += w * (1.5 if in_title else 1.0)

        # Depth: matching several members of one concept (e.g. 'install' AND
        # 'software') is stronger evidence than a single member.
        score += min(1.0, 0.5 * sum(len(set(p)) - 1 for p in member_positions.values()))
        # Adjacency: question concepts appearing next to each other in the
        # body ('personal devices', 'install software') signal a direct hit.
        adj = 0
        gs = list(member_positions)
        for i in range(len(gs)):
            for j in range(i + 1, len(gs)):
                if any(abs(a - b) <= 3 for a in member_positions[gs[i]] for b in member_positions[gs[j]]):
                    adj += 1
        score += min(2.0, float(adj))

        if len(body_hits) >= MIN_BODY_HITS:
            eligible = True
        else:
            # Relaxed path: a clause whose BODY carries obligation language
            # (e.g. "LWP requires approval ...") may answer even when its
            # topic words sit in the heading — but only for approval-intent
            # questions, and never on body-less heading matches alone.
            title_hits = len(hits)
            eligible = (
                len(body_hits) >= 1
                and title_hits >= MIN_BODY_HITS
                and APPROVAL_INTENT.search(question) is not None
                and len(OBLIGATION_MARKERS.findall(body_low)) >= 1
            )
        if not eligible:
            continue
        if APPROVAL_INTENT.search(question):
            score += 2.0 * len(set(OBLIGATION_MARKERS.findall(body_low)))
        if score > best_score:
            best, best_score, best_hits = d, score, hits
    return best, best_score, best_hits


def build_answer(section, question):
    """Quote only the sentences of THIS section that overlap the question,
    plus the sentence immediately following each pick so limits/conditions
    stated in a follow-up sentence are never dropped."""
    groups = question_groups(question)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", section["body"]) if s.strip()]
    overlaps = []
    for i, s in enumerate(sentences):
        low = s.lower()
        overlap = sum(1 for g in groups if group_in(low, g))
        overlaps.append((i, overlap))
    picked_idx = [i for i, ov in overlaps if ov > 0]
    picked_idx.sort(key=lambda i: -overlaps[i][1])
    picked_set = set(picked_idx[:3])
    for i in list(picked_set):  # context continuation
        if i + 1 < len(sentences):
            picked_set.add(i + 1)
    chosen = [sentences[i] for i in sorted(picked_set)][:4]
    if not chosen:
        chosen = sentences[:2]
    citation = "[%s, clause %s]" % (section["doc"], section["id"])
    return "%s %s" % (citation, " ".join(chosen))


def route_team(question):
    for rx, team in TEAM_BY_TOPIC:
        if rx.search(question):
            return team
    return "HR Department"


def contains_hedging(answer):
    low = answer.lower()
    return any(h in low for h in HEDGING_PHRASES)


def answer_question(docs, question):
    """Return (answer_text, cited_section_or_None). Single-source guaranteed.

    Domain routing first: a clearly domain-bound question is answered from
    that ONE document only, so blending two policies is impossible.
    """
    domain = route_domain(question)
    if domain is not None:
        docs = [d for d in docs if d["doc"] == domain]
        if not docs:
            return REFUSAL_TEMPLATE.format(team=route_team(question)), None
    section, score, hits = retrieve(docs, question)
    if section is None or len(hits) < MIN_BODY_HITS or score < 3.0:
        return REFUSAL_TEMPLATE.format(team=route_team(question)), None
    ans = build_answer(section, question)
    if contains_hedging(ans):  # enforcement rule 2 — never emit hedged text
        return REFUSAL_TEMPLATE.format(team=route_team(question)), None
    return ans, section


def run_repl(docs):
    print("Ask My Documents — CMC policies: %s" % ", ".join(POLICY_FILES))
    print("Type a question, 'questions' for the built-in test set, or 'quit'.")
    while True:
        try:
            line = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            print("Bye.")
            break
        if line.lower() in ("questions", "test", "help", "h"):
            for q in TEST_QUESTIONS:
                print("  - %s" % q)
            continue
        ans, sec = answer_question(docs, line)
        print("")
        print(ans)


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents (interactive CLI)")
    parser.add_argument("--question", default=None,
                        help="Ask one question non-interactively (optional; omit for interactive mode)")
    args = parser.parse_args()

    docs = load_documents()
    if not docs:
        print("ERROR: no policy sections indexed")
        sys.exit(1)

    if args.question:
        ans, _ = answer_question(docs, args.question)
        print(ans)
        return

    run_repl(docs)


if __name__ == "__main__":
    main()
