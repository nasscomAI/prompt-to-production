"""
UC-X — Ask My Documents: single-source policy Q&A with citations or refusal.

Policy mode: retrieves from the three policy documents under
../data/policy-documents/, indexes each by document name and section number,
and answers from exactly one section (verbatim text + citation). A question
with no anchor topic in the documents, or below the coverage threshold, is
answered with the exact refusal template. It never blends two documents and
never adds hedging commentary.

Complaint mode: reads a test_<city>.csv complaint file and writes a per-row
classification result_<city>.csv (category, priority, reason, flag). Rows that
cannot be classified are flagged NEEDS_REVIEW rather than guessed.
"""
import argparse
import csv
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
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

EXPANSIONS = {
    "lwp": "leave without pay",
    "lop": "loss of pay",
    "da": "daily allowance",
    "mfa": "multi-factor authentication",
    "byod": "bring your own device",
    "cmc": "city municipal corporation",
}

STOPWORDS = frozenset("""
a an the and or but if then than else when while because
of for in on at to from by with as about after before between during over under above below
is are was were be been being do does did have has had having
can could may might should would will shall must ought
i me my mine you your yours we our ours they their them he his she her it its
what which who whom whose where when why how
this that these those there here
not no nor
use used using allow allowed able
procedure process policy policies rules rule steps guidelines
happens happen happened tell describe explain
many much few some several get takes take long
""".split())

COVERAGE_THRESHOLD = 0.25

WEAK_ANCHORS = frozenset(["working"])

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_SECTION_RE = re.compile(r"^\s*(\d+)\.(\d+)\s+(.*)$")
_HEADER_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")


def retrieve_documents(data_dir):
    """Skill: retrieve_documents — loads the three policy files and indexes
    each by document name and section number.

    input:  directory path (str) containing the policy documents.
    output: {doc_name: [(section_number, section_text), ...]} in file order.
    error_handling: raises FileNotFoundError if a policy file is missing.
    """
    index = {}
    for name in DOC_FILES:
        path = os.path.join(data_dir, name)
        if not os.path.exists(path):
            raise FileNotFoundError("policy document not found: {0}".format(path))
        index[name] = _parse_sections(path)
    return index


def _parse_sections(path):
    sections = []
    current = None
    heading_num = ""
    heading_title = ""
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or not _TOKEN_RE.search(line):
                continue
            h = _HEADER_RE.match(line)
            if h:
                heading_num = h.group(1)
                heading_title = h.group(2).strip()
                current = None
                continue
            m = _SECTION_RE.match(line)
            if m:
                current = {
                    "section": m.group(1) + "." + m.group(2),
                    "heading_num": heading_num,
                    "heading_title": heading_title,
                    "text": [m.group(3).strip()],
                }
                sections.append(current)
                continue
            if current is not None:
                current["text"].append(line.strip())
    return [
        (s["section"], s["heading_num"], s["heading_title"], " ".join(t for t in s["text"] if t))
        for s in sections
    ]


def _build_entries(index):
    entries = []
    order = 0
    for doc, sections in index.items():
        for num, heading_num, heading_title, text in sections:
            entries.append({
                "doc": doc,
                "num": num,
                "heading": heading_title,
                "text": text,
                "variants": _token_variant_set(text),
                "heading_variants": _token_variant_set(heading_title),
                "order": order,
            })
            order += 1
    return entries


def stems(word):
    word = word.lower()
    seen = set()
    stack = [word]
    suffixes = ("es", "ed", "al", "er", "s", "e")
    while stack:
        w = stack.pop()
        if w in seen or len(w) < 2:
            continue
        seen.add(w)
        if len(w) <= 3:
            continue
        if w.endswith("ied") and len(w) > 4:
            stack.append(w[:-3] + "y")
        for suf in suffixes:
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                stack.append(w[: -len(suf)])
    return seen


def _token_variant_set(text):
    variants = set()
    for tok in _TOKEN_RE.findall(text.lower()):
        variants.update(stems(tok))
        expanded = EXPANSIONS.get(tok)
        if expanded:
            for etok in _TOKEN_RE.findall(expanded):
                variants.update(stems(etok))
    return variants


def _matches(question_token, variants):
    if question_token in variants:
        return True
    return any(len(v) >= 4 for v in stems(question_token) & variants)


def _question_tokens(question):
    return [t for t in _TOKEN_RE.findall(question.lower()) if t not in STOPWORDS]


def _coverage(qtokens, entry):
    matched = sum(1 for tok in qtokens if _matches(tok, entry["variants"]))
    return matched / len(qtokens)


def _heading_matches(qtokens, entry):
    return sum(1 for tok in qtokens if _matches(tok, entry["heading_variants"]))


def _anchor_in_heading(anchor, entry):
    return _matches(anchor, entry["heading_variants"])


def answer_question(question, index):
    """Skill: answer_question — returns a single-source answer with citation,
    or the refusal template verbatim.

    input:  question (str), retrieved document index.
    output: "policy_<x>.txt section <n>\n\n<verbatim section text>", or
            REFUSAL_TEMPLATE verbatim.
    error_handling: refuses when the question has no anchor topic in any
    document, or the best match is below the coverage threshold with no
    topic-heading confirmation (e.g. anchor word in the section heading).
    """
    qtokens = _question_tokens(question)
    entries = _build_entries(index)
    if not qtokens:
        return REFUSAL_TEMPLATE

    if not any(_matches(qtokens[0], e["variants"]) for e in entries) or \
       not any(_matches(qtokens[-1], e["variants"]) for e in entries):
        return REFUSAL_TEMPLATE

    anchor = None
    for tok in qtokens:
        if tok in WEAK_ANCHORS:
            continue
        if any(_matches(tok, e["variants"]) for e in entries):
            anchor = tok
            break
    if anchor is None:
        return REFUSAL_TEMPLATE

    candidates = [e for e in entries if _matches(anchor, e["variants"])]
    candidates.sort(key=lambda e: (
        -(_coverage(qtokens, e) + (0.5 if _anchor_in_heading(anchor, e) else 0.0)),
        -_heading_matches(qtokens, e),
        e["order"],
    ))
    best = candidates[0]
    best_coverage = _coverage(qtokens, best)

    if best_coverage < COVERAGE_THRESHOLD and not _anchor_in_heading(anchor, best):
        return REFUSAL_TEMPLATE

    return "{0} section {1}\n\n{2}".format(best["doc"], best["num"], best["text"])


CATEGORIES = [
    ("Flooding", [
        "flood", "floods", "flooded", "flooding", "waterlogged", "water logging",
        "rainwater", "rain water", "submerged", "standing in water", "inundation",
        "channel rainwater", "inaccessible",
    ]),
    ("Drainage", [
        "drain", "drains", "drainage", "draining", "sewer", "sewage", "gutter",
        "gutter", "manhole", "blocked", "clog", "clogged", "choke", "choked",
    ]),
    ("Pothole", [
        "pothole", "potholes",
    ]),
    ("Road Damage", [
        "road surface", "road collapsed", "road subsided", "road subsidence",
        "road buckled", "cracked road", "sinking", "subsidence", "subsided",
        "buckled", "footpath", "paving", "paved", "cobblestone", "cobblestones",
        "broken road", "collapsed",
    ]),
    ("Heat Hazard", [
        "heat", "hot", "hotter", "sun", "sunlight", "temperature",
        "temperature", "melting", "melted", "melt", "scorching", "scorch",
        "burning", "burns", "burn", "heatwave", "heat wave", "sweltering",
        "unbearable", "bubbling", "sweating",
    ]),
    ("Tree Hazard", [
        "tree", "trees", "branch", "branches", "fallen tree",
    ]),
    ("Waste", [
        "garbage", "waste", "wastes", "trash", "litter", "rubbish", "dumping",
        "dump", "dumped", "debris", "overflow", "overflowing", "overflowed",
        "bins", "bin", "dead animal", "refuse",
    ]),
    ("Streetlight", [
        "streetlight", "streetlights", "street light", "street lights", "lamp",
        "lamps", "lamppost", "lampposts", "lamp post", "lighting", "lights",
        "lights out", "unlit", "darkness", "dark", "substation", "flickering",
        "sparking", "electrical hazard",
    ]),
    ("Noise", [
        "noise", "noises", "noisy", "loud", "louder", "music", "amplifier",
        "amplifiers", "drilling", "honk", "honking", "engines", "idling",
        "band", "wedding",
    ]),
    ("Heritage Damage", [
        "heritage", "ancient", "historic", "historical", "monument", "monuments",
        "museum", "palace", "fort", "tomb", "statue",
    ]),
    ("Infrastructure", [
        "irrigation", "bench", "shelter", "glass", "divider", "dividers",
        "walkway", "railing", "tiles",
    ]),
]

SEVERITY_KEYWORDS = [
    "injury", "injuries", "injured", "child", "children", "school", "schools",
    "hospital", "hospitals", "hospitalised", "hospitalized", "ambulance",
    "fire", "hazard", "hazards", "fell", "fallen", "collapse", "collapsed",
    "collapsing", "risk", "unsafe", "danger", "dangerous", "leak", "sparking",
    "blowout", "lives", "stranded", "crisis", "emergency",
]

LOW_PHRASES = [
    "no action", "no need", "just informing", "just to inform",
    "informational", "no issue", "no problem", "for information",
]


def _has(text, keyword):
    low = text.lower()
    low_kw = keyword.lower()
    if " " in low_kw:
        return low_kw in low
    return re.search(r"\b" + re.escape(low_kw) + r"\b", low) is not None


def _classify_complaint(description):
    for cat, keywords in CATEGORIES:
        for kw in keywords:
            if _has(description, kw):
                return cat, kw
    return "Other", None


def _priority(description):
    if any(_has(description, kw) for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    if any(phrase in description.lower() for phrase in LOW_PHRASES):
        return "Low"
    return "Standard"


def _pick_column(fieldnames, candidates, rows):
    """Pick the field that best matches candidates, else the longest-text field."""
    for name in fieldnames:
        if name.strip().lower() in candidates:
            return name
    if rows:
        return max(
            fieldnames,
            key=lambda f: sum(len((r.get(f) or "")) for r in rows) / len(rows),
        )
    return fieldnames[0] if fieldnames else None


def _default_output(input_path):
    stem = os.path.splitext(os.path.basename(input_path))[0]
    if stem.startswith("test_"):
        stem = stem[len("test_"):]
    return "result_{0}.csv".format(stem)


def analyze_complaints(input_path, output_path):
    """Skill: analyze_complaints — classifies every complaint row in a
    test_<city>.csv and writes a per-row result CSV.

    input:  path to a complaint CSV with a description column.
    output: CSV with complaint_id, category, priority, reason, flag.
    error_handling: rows with no supported category or missing description are
    flagged NEEDS_REVIEW; the reason always names the matched keyword or says
    why the row needs review — never a guess.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    desc_col = _pick_column(
        fieldnames,
        {"description", "complaint_description", "complaint", "issue",
         "details", "text", "problem", "what happened", "incident"},
        rows,
    )
    id_col = _pick_column(
        fieldnames,
        {"complaint_id", "id", "ticket", "ticket_id", "case_id", "reference"},
        rows,
    )

    results = []
    for row in rows:
        complaint_id = row.get(id_col) if id_col else ""
        description = (row.get(desc_col) or "").strip() if desc_col else ""
        if not description:
            results.append({
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Standard",
                "reason": "Description is missing or empty; flagged for review.",
                "flag": "NEEDS_REVIEW",
            })
            continue
        category, snippet = _classify_complaint(description)
        flag = ""
        if category == "Other":
            flag = "NEEDS_REVIEW"
            excerpt = description if len(description) <= 60 else description[:60] + "..."
            reason = (
                "No supported category matches the description "
                "('{0}'), so it is classified as Other for review.".format(excerpt)
            )
        else:
            reason = (
                "The description mentions '{0}', which indicates "
                "the {1} category.".format(snippet, category)
            )
        results.append({
            "complaint_id": complaint_id,
            "category": category,
            "priority": _priority(description),
            "reason": reason,
            "flag": flag,
        })

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-X policy Q&A and city complaint classifier"
    )
    parser.add_argument("--data-dir", default=os.path.join("..", "data", "policy-documents"))
    parser.add_argument("--question", help="Answer one question and exit (default: interactive)")
    parser.add_argument("--input", help="Complaint CSV to classify (test_<city>.csv)")
    parser.add_argument("--output", help="Output results CSV (default: result_<city>.csv in current dir)")
    args = parser.parse_args()

    if args.input:
        output = args.output or _default_output(args.input)
        analyze_complaints(args.input, output)
        print("Done. Results written to {0}".format(output))
        return

    try:
        index = retrieve_documents(args.data_dir)
    except (FileNotFoundError, OSError) as exc:
        sys.exit("REFUSE: {0}".format(exc))

    total = sum(len(sections) for sections in index.values())
    sys.stderr.write("Loaded {0} sections from {1} policy documents.\n".format(total, len(index)))

    if args.question:
        print(answer_question(args.question, index))
        return

    print("Ask a policy question. Type 'quit' to exit.")
    for raw in sys.stdin:
        question = raw.strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
