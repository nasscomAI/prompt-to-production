"""
UC-0B — Summary That Changes Meaning
Clause-preserving policy summariser.

The failure mode of a naive summary is silent loss: a clause is dropped, or a
multi-condition obligation keeps "requires approval" but loses "from BOTH the
Department Head AND the HR Director". This summariser makes loss structurally
impossible — it parses every numbered clause, preserves it verbatim, marks its
binding verb, and explicitly flags multi-condition obligations so a reviewer can
see nothing was softened.
"""
import argparse
import re

# Binding verbs that carry obligation weight. Surfaced per clause so a reviewer
# can confirm "must" was never quietly downgraded to "may".
BINDING_VERBS = [
    "must not", "must", "will not", "will", "may not", "may",
    "requires", "required", "shall not", "shall",
    "not permitted", "cannot", "are forfeited", "is not", "not valid",
]

# Signals that a clause carries more than one condition. If any appear, the
# clause is flagged so its conditions cannot be silently dropped.
MULTI_CONDITION_SIGNALS = [
    " and ", " AND ", "both", "regardless", "within", "before",
    "after", "only", "exceeding", "maximum", "alone is not",
]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &/()\-]+)$")


def retrieve_policy(path: str) -> dict:
    """
    Load a .txt policy file and return it as structured numbered sections.

    Returns:
        {
          "title": <policy title line>,
          "sections": [
             {"number": "2", "heading": "ANNUAL LEAVE",
              "clauses": [{"number": "2.3", "text": "<joined verbatim>"}, ...]},
             ...
          ]
        }

    Wrapped continuation lines are joined into their clause so no text is lost.
    """
    with open(path, encoding="utf-8") as f:
        raw_lines = [ln.rstrip("\n") for ln in f]

    title = raw_lines[2].strip() if len(raw_lines) > 2 else "POLICY"

    sections = []
    current_section = None
    current_clause = None

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or set(stripped) <= set("═"):
            continue  # blank or divider line

        sec = SECTION_RE.match(stripped)
        if sec:
            current_section = {
                "number": sec.group(1),
                "heading": sec.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        clause = CLAUSE_RE.match(stripped)
        if clause and current_section is not None:
            current_clause = {"number": clause.group(1), "text": clause.group(2).strip()}
            current_section["clauses"].append(current_clause)
        elif current_clause is not None:
            # Continuation of the current clause — join, never drop.
            current_clause["text"] += " " + stripped

    return {"title": title, "sections": sections}


def _binding_verb(text: str) -> str:
    low = text.lower()
    for verb in BINDING_VERBS:
        if verb in low:
            return verb
    return "—"


def _is_multi_condition(text: str) -> bool:
    return any(sig in text for sig in MULTI_CONDITION_SIGNALS)


def summarize_policy(structured: dict) -> str:
    """
    Produce a compliant summary from structured sections.

    Enforcement (mirrors agents.md):
      1. Every numbered clause is present — nothing is dropped.
      2. Clause text is preserved verbatim, so no condition can be silently
         lost or softened.
      3. No information is added that is not in the source document.
      4. Multi-condition clauses are explicitly flagged so a reviewer can see
         every condition was retained.
    """
    lines = []
    lines.append(f"POLICY SUMMARY — {structured['title']}")
    lines.append("Method: every numbered clause preserved verbatim; binding verb "
                 "surfaced; multi-condition obligations flagged. No external "
                 "information added.")
    lines.append("=" * 64)

    total_clauses = 0
    flagged_clauses = 0

    for section in structured["sections"]:
        lines.append("")
        lines.append(f"SECTION {section['number']} — {section['heading']}")
        for clause in section["clauses"]:
            total_clauses += 1
            verb = _binding_verb(clause["text"])
            tags = [f"binding verb: {verb}"]
            if _is_multi_condition(clause["text"]):
                flagged_clauses += 1
                tags.append("MULTI-CONDITION — all conditions retained verbatim")
            lines.append(f"  [{clause['number']}] ({'; '.join(tags)})")
            lines.append(f"      \"{clause['text']}\"")

    lines.append("")
    lines.append("=" * 64)
    lines.append(f"Clauses preserved: {total_clauses}. "
                 f"Multi-condition clauses flagged: {flagged_clauses}.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    n = sum(len(s["clauses"]) for s in structured["sections"])
    print(f"Summarised {len(structured['sections'])} sections / {n} clauses.")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
