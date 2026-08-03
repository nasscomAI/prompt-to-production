"""
UC-0B app.py

Produces a compliant, clause-referenced SUMMARY of an HR / policy document.

Design goal (see agents.md / skills.md / README.md):
  - Every numbered clause in the source must appear in the summary.
  - All conditions of multi-condition obligations must be preserved.
  - Binding verbs (must / will / requires / not permitted / cannot ...) must
    never be softened or dropped.
  - No information may be added that is not in the source (no scope bleed).
  - If — and only if — a clause cannot be compressed without losing a critical
    token, it is quoted verbatim and flagged. Verbatim is the EXCEPTION, not the
    default (README rule 4).

Approach (deterministic, matching the UC-0A pattern — no LLM at runtime):
  1. retrieve_policy parses the source into structured, numbered clauses.
  2. summarize_policy compresses each clause with a fixed set of
     meaning-preserving transforms, then VALIDATES that every critical token
     (numbers, binding verbs, named roles/forms, negations) survived.
       - Validation passes  -> emit the shorter, compressed line.
       - Validation fails    -> emit the clause verbatim with a [VERBATIM] flag.
  Because the compressed text is validated against the source's critical tokens,
  a condition can never be silently dropped and an obligation can never be
  silently softened: any such loss forces the safe verbatim fallback.
"""
import argparse
import re
import sys

# ---------------------------------------------------------------------------
# Parsing constants
# ---------------------------------------------------------------------------

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-/()]+)$")
SEPARATOR_RE = re.compile(r"^[═=\-\s]+$")

# ---------------------------------------------------------------------------
# Meaning-preserving compression transforms (applied in order).
# Each maps a verbose phrase to a shorter equivalent WITHOUT dropping any
# number, binding verb, named role, or negation. Validation is the safety net.
# ---------------------------------------------------------------------------

COMPRESSIONS = [
    (r"\bup to a maximum of\b", "max"),
    (r"\ba maximum of\b", "max"),
    (r"\bmaximum of\b", "max"),
    # Numeric bounds only — require a number (optionally "Rs") to follow, so
    # idioms like "up to and including" are never touched.
    (r"\bat least\b(?=\s+(?:Rs\s*)?\d)", "\u2265"),   # ≥
    (r"\bup to\b(?=\s+(?:Rs\s*)?\d)", "\u2264"),       # ≤
    (r"\bper calendar year\b", "/year"),
    (r"\bper financial year\b", "/FY"),
    (r"\bper night\b", "/night"),
    (r"\bper day\b", "/day"),
    (r"\bper month\b", "/month"),
    (r"\bis entitled to\b", "gets"),
    (r"\bare entitled to\b", "get"),
    (r"\bin the course of official duties\b", "on official duties"),
    (r"\bfrom the date of joining\b", "from joining"),
    (r"\bof returning to work\b", "of return"),
    (r"\bthe following calendar year\b", "next year"),
    (r"\bwithin the first quarter \(January\u2013March\) of the following year\b",
     "in Jan\u2013Mar next year"),
]

# Binding / obligation vocabulary that must survive compression intact.
BINDING_KEYWORDS = [
    "must", "will", "requires", "require", "required", "mandatory",
    "not permitted", "not valid", "not sufficient", "not reimbursable",
    "not eligible", "not accepted", "cannot", "not be", "not use", "not share",
    "not install", "not forward", "not count", "not apply", "forfeited",
    "disciplinary offence", "only", "without",
]

# Negation words whose presence must be preserved (dropping one flips meaning).
NEGATIONS = ["not", "never", "cannot", "no ", "without", "only"]


# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(input_path):
    """Load a .txt policy file and parse it into a structured document.

    Returns: {"title": str, "sections": [{"number","title","clauses":[...]}]}
    Clause text is captured verbatim; the title is taken verbatim from the
    source header (never invented).
    """
    try:
        with open(input_path, "r", encoding="utf-8") as fh:
            raw_lines = fh.read().splitlines()
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot read input file '{input_path}': {exc}")

    sections = []
    header_lines = []
    current_section = None
    current_clause = None

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        clause_match = CLAUSE_RE.match(stripped)

        if clause_match:
            current_clause = {
                "number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            if current_section is None:
                current_section = {"number": "0", "title": "GENERAL", "clauses": []}
                sections.append(current_section)
            current_section["clauses"].append(current_clause)
        elif section_match:
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
        else:
            if current_clause is not None:
                current_clause["text"] = (current_clause["text"] + " " + stripped).strip()
            elif current_section is None:
                header_lines.append(stripped)

    title = ""
    for candidate in header_lines:
        if "POLICY" in candidate.upper() and not candidate.upper().startswith("DOCUMENT"):
            title = candidate
            break
    if not title and header_lines:
        title = header_lines[0]
    if not title:
        title = "POLICY"

    return {"title": title, "sections": sections}


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy
# ---------------------------------------------------------------------------

def _critical_tokens(text):
    """Extract the tokens that must survive compression, from the source clause."""
    lowered = text.lower()
    tokens = {"numbers": [], "binding": [], "names": [], "negations": []}

    # Numbers (keep commas, e.g. 3,500). Order preserved.
    tokens["numbers"] = re.findall(r"\d[\d,]*", text)

    # Binding vocabulary actually present in this clause.
    tokens["binding"] = [kw for kw in BINDING_KEYWORDS if kw in lowered]

    # Named roles / departments (2+ capitalised words), codes/forms, and acronyms.
    multiword = re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b", text)
    codes = re.findall(r"\b[A-Z]{2,}[-\w]*\d[\w-]*\b", text)   # e.g. HR-L1, FIN-T1
    acronyms = re.findall(r"\b[A-Z]{2,}\b", text)              # e.g. LOP, DA, MFA, LWP
    tokens["names"] = list(dict.fromkeys(multiword + codes + acronyms))

    # Negation presence.
    tokens["negations"] = [n for n in NEGATIONS if n in lowered]

    return tokens


def _compress(text):
    out = text
    for pattern, repl in COMPRESSIONS:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    out = re.sub(r"\s+", " ", out).strip()
    return out


# Whole phrases/words to UPPERCASE for emphasis on a critical clause, so the
# binding force is visually preserved. Phrases first, then single words.
EMPHASIS_PHRASES = [
    "not permitted", "not valid", "not sufficient", "not reimbursable",
    "not eligible", "not accepted", "are forfeited", "is forfeited",
]
EMPHASIS_WORDS = [
    "must", "will", "requires", "require", "required", "mandatory",
    "cannot", "never", "not", "only", "both", "forfeited",
]


def _emphasize(text):
    """Uppercase binding vocabulary in a critical clause for visual emphasis.

    Case-only change: it never alters, adds, or removes tokens, so validation
    (which compares case-insensitively) is unaffected.
    """
    out = text
    for phrase in EMPHASIS_PHRASES:
        out = re.sub(re.escape(phrase), phrase.upper(), out, flags=re.IGNORECASE)
    for word in EMPHASIS_WORDS:
        out = re.sub(rf"\b{word}\b", word.upper(), out, flags=re.IGNORECASE)
    # "both X and Y" — uppercase the connective AND only in a "both" context.
    if re.search(r"\bBOTH\b", out):
        out = re.sub(r"\band\b", "AND", out)
    return out


def _is_critical(source):
    """A clause is critical if it carries a binding verb, a negation, or a
    multi-part condition (approver/deadline/exclusion). Descriptive clauses
    (entitlements, accrual facts, plain scope) can be safely grouped."""
    crit = _critical_tokens(source)
    if crit["binding"] or crit["negations"]:
        return True
    # Two or more numbers plus a joining/condition word => layered condition.
    if len(crit["numbers"]) >= 2 and re.search(
        r"\b(and|or|before|after|within|regardless|between)\b", source, re.IGNORECASE
    ):
        return True
    return False


def _passes_validation(source, compressed):
    """True only if every critical token from the source survives in `compressed`."""
    crit = _critical_tokens(source)
    low = compressed.lower()

    for num in crit["numbers"]:
        if num not in compressed:
            return False
    for kw in crit["binding"]:
        if kw not in low:
            return False
    for name in crit["names"]:
        if name not in compressed:
            return False
    # Negations: count must not drop (compression must not remove a "not"/"no"/etc).
    for neg in crit["negations"]:
        if source.lower().count(neg) > low.count(neg):
            return False
    return True


def _render_clause(source):
    """Return (rendered_line_body, was_verbatim) for a single clause.

    Tries compression; validates; falls back to verbatim on validation failure.
    """
    compressed = _compress(source)
    if _passes_validation(source, compressed):
        body = compressed if len(compressed) < len(source) else source
        return body, False
    return f'[VERBATIM \u2014 could not compress without meaning loss] "{source}"', True


def summarize_policy(document):
    """Produce a two-tier, clause-referenced summary of the structured document.

    - DESCRIPTIVE clauses (entitlements, accrual facts, plain scope) are
      compressed and grouped by section into a single condensed line — this is
      where real summarization happens.
    - CRITICAL clauses (binding verbs, negations, multi-part conditions) are kept
      individually, tagged [CRITICAL], emphasised (binding words UPPERCASED), and
      validated token-by-token so no condition is dropped or obligation softened.
    - Any clause whose compression fails validation is quoted verbatim and flagged
      (the exception path). No new information is ever introduced.
    """
    sections = document["sections"]
    if not sections:
        raise SystemExit("ERROR: no sections parsed; refusing to emit a partial summary.")

    lines = [
        f"{document['title']} \u2014 SUMMARY",
        "Two-tier: descriptive clauses grouped & condensed; [CRITICAL] clauses kept",
        "individually with binding words UPPERCASED. Every clause is validated against",
        "the source (numbers, binding verbs, named approvers, negations preserved).",
        "",
    ]

    total = 0
    critical_count = 0
    verbatim = 0
    src_chars = 0
    out_chars = 0

    for section in sections:
        lines.append(f"{section['number']}. {section['title']}")

        descriptive = []       # (number, compressed_body) — grouped, non-binding
        critical_lines = []    # rendered [CRITICAL] / verbatim lines, in order
        for clause in section["clauses"]:
            total += 1
            number = clause["number"]
            source = re.sub(r"\s+", " ", clause["text"]).strip()
            src_chars += len(source)
            body, was_verbatim = _render_clause(source)

            if _is_critical(source):
                critical_count += 1
                if was_verbatim:
                    verbatim += 1
                    out_chars += len(source)
                    critical_lines.append(f"  - Clause {number} {body}")
                else:
                    out_chars += len(body)
                    critical_lines.append(f"  - Clause {number} [CRITICAL]: {_emphasize(body)}")
            else:
                if was_verbatim:
                    verbatim += 1
                    out_chars += len(source)
                    critical_lines.append(f"  - Clause {number} {body}")
                else:
                    descriptive.append((number, body))

        # Descriptive summary first (context), then the itemised critical clauses.
        if descriptive:
            nums = ", ".join(n for n, _ in descriptive)
            label = "Clause" if len(descriptive) == 1 else "Clauses"
            merged = "; ".join(b.rstrip(".") for _, b in descriptive) + "."
            out_chars += len(merged)
            lines.append(f"  - {label} {nums}: {merged}")
        lines.extend(critical_lines)

        lines.append("")

    reduction = (1 - out_chars / src_chars) * 100 if src_chars else 0.0
    lines.append("---")
    lines.append(f"Clauses represented: {total} (critical: {critical_count}, descriptive: {total - critical_count})")
    lines.append(f"Quoted verbatim (exception): {verbatim}")
    lines.append(f"Character reduction vs source clauses: {reduction:.1f}%")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Summarize a policy without dropping clauses or softening obligations."
    )
    parser.add_argument("--input", required=True, help="Path to the input .txt policy file.")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file.")
    args = parser.parse_args()

    document = retrieve_policy(args.input)
    summary = summarize_policy(document)

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(summary)
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot write output file '{args.output}': {exc}")

    clause_count = sum(len(s["clauses"]) for s in document["sections"])
    print(f"Wrote summary of {clause_count} clauses to '{args.output}'.", file=sys.stderr)


if __name__ == "__main__":
    main()
