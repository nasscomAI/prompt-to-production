"""
UC-0B — Policy summariser (compliance-safe).

Reads a numbered policy .txt file and emits a summary in which:
  * every numbered clause is present, labelled with its clause number
  * binding verbs (must / requires / will / not permitted / may / cannot)
    are preserved verbatim
  * multi-condition rules keep every condition
  * no hedging or generic phrasing is added

See agents.md for the enforcement rules this implements.
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Optional


# Forbidden hedging / scope-bleed phrases — the summariser MUST NOT emit these.
FORBIDDEN_PHRASES = [
    "typically",
    "in general",
    "as is standard practice",
    "employees are generally expected to",
    "usually",
    "often",
    "commonly",
    "it is understood that",
    "as a rule of thumb",
]

# Binding verbs — presence in a clause is preserved as a tag.
# Order matters: the first pattern that matches wins (most-specific first).
BINDING_VERB_PATTERNS: list[tuple[str, str]] = [
    (r"\bnot permitted\b", "NOT PERMITTED"),
    (r"\bmust not\b", "MUST NOT"),
    (r"\bcannot\b|\bcan not\b", "CANNOT"),
    (r"\brequires\b|\brequired\b", "REQUIRES"),
    (r"\bmust\b", "MUST"),
    (r"\bwill be\b|\bwill\b", "WILL"),
    (r"\bmay not\b", "MAY NOT"),
    (r"\bmay\b", "MAY"),
    (r"\bare entitled to\b|\bis entitled to\b|\bentitled to\b", "ENTITLED"),
    (r"\bare forfeited\b|\bis forfeited\b|\bforfeited\b", "FORFEITED"),
]

# Clause number pattern: N.M at the start of a line (allowing indentation).
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.+)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 &()/-]+)\s*$")


def retrieve_policy(path: str) -> dict:
    """Parse the policy file into a structured dict of sections and clauses."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        sys.exit(f"ERROR: cannot open policy file '{path}': {e}")

    header_lines: list[str] = []
    sections: list[dict] = []
    current_section: Optional[dict] = None
    current_clause: Optional[dict] = None
    in_body = False

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        # Skip decorative separators.
        if stripped and set(stripped) <= {"═", "─", "=", "-"}:
            continue

        # Section header: "1. PURPOSE AND SCOPE"
        m_section = SECTION_RE.match(line)
        if m_section:
            in_body = True
            current_clause = None
            current_section = {
                "number": m_section.group(1),
                "title": m_section.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        # Clause: "2.3 Employees must submit a leave application ..."
        m_clause = CLAUSE_RE.match(line)
        if m_clause and current_section is not None:
            current_clause = {
                "number": m_clause.group(1),
                "text": m_clause.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            continue

        # Continuation of the current clause (indented wrap-around lines).
        if current_clause is not None and stripped:
            current_clause["text"] = (current_clause["text"] + " " + stripped).strip()
            continue

        # Pre-body header block (document reference, version, etc).
        if not in_body and stripped:
            header_lines.append(stripped)

    if not any(sec["clauses"] for sec in sections):
        sys.exit(f"ERROR: no numbered clauses found in '{path}'. Refusing to emit empty summary.")

    return {"header": header_lines, "sections": sections}


def _detect_binding_verbs(clause_text: str) -> list[str]:
    tags: list[str] = []
    for pattern, tag in BINDING_VERB_PATTERNS:
        if re.search(pattern, clause_text, flags=re.IGNORECASE) and tag not in tags:
            tags.append(tag)
    return tags


def _has_multiple_conditions(clause_text: str) -> bool:
    """
    Heuristic: a clause has multi-conditions if it joins two named entities
    with 'and' near a binding verb, or explicitly says 'both'.
    """
    text = clause_text.lower()
    if "both" in text and "and" in text:
        return True
    # Approval from X and Y pattern.
    if re.search(r"approval from .*\band\b.*", text):
        return True
    # X and Y (both proper-noun-ish) approval / approver mention.
    if re.search(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+and\s+the\s+[A-Z]", clause_text):
        return True
    return False


def _assert_no_forbidden(text: str, clause_no: str) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            sys.exit(
                f"ERROR: clause {clause_no} summary contains forbidden hedging "
                f"phrase '{phrase}'. Aborting to protect meaning."
            )


def summarize_policy(policy: dict) -> str:
    """Render the structured policy as a compliance-safe summary string."""
    out: list[str] = []
    out.append("═══════════════════════════════════════════════════════════")
    out.append("POLICY SUMMARY — generated under agents.md enforcement rules")
    out.append("═══════════════════════════════════════════════════════════")
    if policy["header"]:
        out.append("")
        out.append("Source header:")
        for h in policy["header"]:
            out.append(f"  {h}")
    out.append("")
    out.append(
        "Every numbered clause below is preserved verbatim so no obligation "
        "can be lost in paraphrase. Each line is tagged with its binding verb."
    )
    out.append("")

    for section in policy["sections"]:
        out.append("")
        out.append(f"── Section {section['number']}: {section['title']} ──")
        if not section["clauses"]:
            out.append("  (no numbered clauses in this section)")
            continue
        for clause in section["clauses"]:
            tags = _detect_binding_verbs(clause["text"])
            tag_str = ", ".join(tags) if tags else "STATEMENT"
            multi = " [MULTI-CONDITION — every condition preserved]" if _has_multiple_conditions(clause["text"]) else ""

            _assert_no_forbidden(clause["text"], clause["number"])

            out.append(f"  Clause {clause['number']} [{tag_str}]{multi}")
            out.append(f"    {clause['text']}")

    out.append("")
    out.append("── End of summary ──")
    return "\n".join(out) + "\n"


def _verify_completeness(policy: dict, summary: str) -> None:
    """Fail loudly if any clause number from the source is missing in the summary."""
    missing: list[str] = []
    for section in policy["sections"]:
        for clause in section["clauses"]:
            if clause["number"] not in summary:
                missing.append(clause["number"])
    if missing:
        sys.exit(
            "ERROR: summary is missing clauses: "
            f"{missing}. Enforcement rule 1 violated."
        )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    p.add_argument("--input", required=True, help="Path to policy .txt file")
    p.add_argument("--output", required=True, help="Path to write summary text file")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    _verify_completeness(policy, summary)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    clause_count = sum(len(s["clauses"]) for s in policy["sections"])
    print(
        f"[app] wrote summary of {clause_count} clauses across "
        f"{len(policy['sections'])} sections to {args.output}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
