"""
UC-0B app.py — policy summariser.

Implements retrieve_policy and summarize_policy per skills.md, enforcing
the fidelity rules in agents.md.

Design choice: no LLM call. Each clause is emitted verbatim. Clauses
carrying one or more binding verbs are prefixed with a tag naming those
verbs in the form [must], [requires], or [may / forfeited] — matching
the "Binding verb" column in README.md. The tag is the verb itself, not
a generic flag, so a reader can see which obligation strength governs
each clause without re-reading the text.
"""
import argparse
import re
import sys
from pathlib import Path

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\d+\.\s+(.+)$")

# (regex, canonical label). Order matters only for tie-breaking when two
# patterns match the same span — the first one in the list wins.
BINDING_VERB_PATTERNS = (
    (r"\bmust\b", "must"),
    (r"\bwill\b", "will"),
    (r"\brequires?\b", "requires"),
    (r"\bmay\b", "may"),
    (r"\bcannot\b", "cannot"),
    (r"\b(?:are|is)\s+forfeited\b", "are forfeited"),
    (r"\bforfeited\b", "are forfeited"),
    (r"\bmandatory\b", "mandatory"),
    (r"\breserves the right\b", "reserves the right"),
    (r"\b(?:is|are) entitled\b", "entitled"),
    (r"\b(?:is|are) required\b", "required"),
    (r"\b(?:is|are) permitted\b", "permitted"),
    (r"\b(?:is|are) reimbursable\b", "reimbursable"),
    (r"\bnot permitted\b", "not permitted"),
    (r"\bnot reimbursable\b", "not reimbursable"),
    (r"\bnot eligible\b", "not eligible"),
    (r"\bnot valid\b", "not valid"),
    (r"\bnot accepted\b", "not accepted"),
    (r"\bnot allowed\b", "not allowed"),
    (r"\bnot sufficient\b", "not sufficient"),
    (r"\bnot considered\b", "not considered"),
    (r"\bonly if\b", "only if"),
    (r"\bprovided (?:that|it)\b", "provided"),
    (r"\b(?:does|do) not apply\b", "does not apply"),
    (r"\b(?:does|do) not cover\b", "does not cover"),
)
COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), label)
                     for p, label in BINDING_VERB_PATTERNS]


def retrieve_policy(path):
    """Load a numbered .txt policy and return clauses in source order."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"policy file not found: {path}")
    raw = p.read_text(encoding="utf-8")

    clauses = []
    seen = set()
    section = None
    current = None

    for line in raw.splitlines():
        bare = line.strip()
        if not bare or bare.startswith("═"):
            if current and not bare:
                pass
            continue

        clause_m = CLAUSE_RE.match(bare)
        if clause_m:
            if current:
                clauses.append(current)
            num = clause_m.group(1)
            if num in seen:
                raise ValueError(f"duplicate clause {num}")
            seen.add(num)
            current = {
                "clause": num,
                "section": section,
                "text": clause_m.group(2).strip(),
            }
            continue

        section_m = SECTION_RE.match(bare)
        if section_m:
            if current:
                clauses.append(current)
                current = None
            section = section_m.group(1).strip()
            continue

        if current:
            current["text"] = current["text"] + " " + bare

    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError("no numbered clauses found")

    for c in clauses:
        c["text"] = re.sub(r"\s+", " ", c["text"]).strip()
    return clauses


def _detect_binding_verbs(text):
    """Return the binding-verb labels present in `text`, in source order, deduped.

    A clause may have several (e.g. README's "may / are forfeited" for 2.6).
    Overlapping matches are resolved to the longest span at each position so
    that "not permitted" wins over a bare "permitted" inside it.
    """
    hits = []  # (start, end, label)
    for regex, label in COMPILED_PATTERNS:
        for m in regex.finditer(text):
            hits.append((m.start(), m.end(), label))
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))

    selected = []
    last_end = -1
    for start, end, label in hits:
        if start < last_end:
            continue
        selected.append((start, label))
        last_end = end

    seen = set()
    ordered = []
    for _, label in selected:
        if label not in seen:
            seen.add(label)
            ordered.append(label)
    return ordered


def summarize_policy(clauses):
    """Produce the fidelity-preserving summary string per skills.md."""
    if not clauses:
        raise ValueError("no clauses to summarise")

    lines = []
    last_section = None
    for c in clauses:
        if c["section"] and c["section"] != last_section:
            if lines:
                lines.append("")
            lines.append(f"## {c['section']}")
            last_section = c["section"]

        verbs = _detect_binding_verbs(c["text"])
        if verbs:
            tag = " / ".join(verbs)
            lines.append(f"{c['clause']} [{tag}] {c['text']}")
        else:
            lines.append(f"{c['clause']} {c['text']}")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="UC-0B policy summariser")
    ap.add_argument("--input", required=True, help="path to .txt policy file")
    ap.add_argument("--output", required=True, help="path to write summary")
    args = ap.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"wrote {len(clauses)} clauses to {args.output}")


if __name__ == "__main__":
    main()
