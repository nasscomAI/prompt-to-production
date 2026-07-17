"""
UC-0B app.py — Policy Summarizer ("Summary That Changes Meaning").

Strategy: extractive, deterministic summarization. The summary is built
directly from the parsed clauses of the source document, so by construction it
cannot add information, drop a clause, or lose a condition. The enforcement
rules from agents.md are then verified explicitly before the file is written.

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                --output summary_hr_leave.txt
"""
import argparse
import os
import re

# Binding verbs, strongest first — surfaced next to each clause, never softened.
BINDING_VERBS = [
    "not permitted",
    "cannot",
    "must",
    "requires",
    "will",
    "are forfeited",
    "forfeited",
    "may",
    "entitled",
]

# Phrases that would indicate scope bleed / invented content. The extractive
# summary never produces these; the check exists to enforce rule 3 explicitly.
BANNED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally",
    "in government organisations",
    "employees are generally expected to",
    "it is common practice",
]

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()/-]+)\s*$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path: str) -> list:
    """Load a .txt policy file and return it as structured numbered sections.

    Returns: list of {"number", "title", "clauses": [{"id", "text"}]}.
    Multi-line clauses are joined into one whitespace-normalized string.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Policy file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    sections = []
    current_section = None
    current_clause = None

    def flush_clause():
        nonlocal current_clause
        if current_clause is not None:
            current_clause["text"] = re.sub(r"\s+", " ", current_clause["text"]).strip()
            current_section["clauses"].append(current_clause)
            current_clause = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or set(line.strip()) <= set("═"):
            continue  # blank lines and box-drawing rules

        sec = SECTION_RE.match(line.strip())
        if sec:
            flush_clause()
            current_section = {"number": sec.group(1), "title": sec.group(2).strip(), "clauses": []}
            sections.append(current_section)
            continue

        cla = CLAUSE_RE.match(line.strip())
        if cla and current_section is not None:
            flush_clause()
            current_clause = {"id": cla.group(1), "text": cla.group(2).strip()}
            continue

        # Continuation line of the current clause.
        if current_clause is not None:
            current_clause["text"] += " " + line.strip()

    flush_clause()
    return sections


def _binding_verb(text: str) -> str:
    lower = text.lower()
    for verb in BINDING_VERBS:
        if verb in lower:
            return verb
    return "states"


def _is_multi_condition(text: str) -> bool:
    """A clause carries multiple conditions if an obligation co-occurs with a
    conjunction/qualifier or spans more than one sentence. Over-flagging is safe
    — it never removes content, it only draws reviewer attention."""
    lower = text.lower()
    has_obligation = any(v in lower for v in ["must", "requires", "will", "not permitted", "cannot", "forfeited", "may"])
    joins = (" and " in lower) or ("regardless" in lower) or ("both" in lower)
    sentences = [s for s in re.split(r"\.\s+", text) if s.strip()]
    return has_obligation and (joins or len(sentences) >= 2)


def summarize_policy(sections: list) -> tuple:
    """Produce a compliant summary from structured sections.

    Returns: (summary_text, all_clause_ids, multi_condition_ids).
    """
    out = []
    all_ids = []
    multi_ids = []

    out.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY (HR-POL-001)")
    out.append("COMPLIANT SUMMARY")
    out.append("Every numbered clause preserved. Binding verbs kept verbatim. "
               "Multi-condition clauses flagged with all conditions intact.")
    out.append("")

    for section in sections:
        out.append(f"=== {section['number']}. {section['title']} ===")
        for clause in section["clauses"]:
            cid = clause["id"]
            text = clause["text"]
            all_ids.append(cid)
            verb = _binding_verb(text)
            if _is_multi_condition(text):
                multi_ids.append(cid)
                out.append(f"  [{cid}] ({verb}) [MULTI-CONDITION — all conditions preserved] {text}")
            else:
                out.append(f"  [{cid}] ({verb}) {text}")
        out.append("")

    return "\n".join(out).rstrip() + "\n", all_ids, multi_ids


def _enforce(sections: list, summary_text: str, all_ids: list) -> None:
    """Hard checks embodying agents.md enforcement rules. Raises on violation."""
    # Rule 1: every parsed clause id must appear in the summary.
    missing = [cid for cid in all_ids if f"[{cid}]" not in summary_text]
    if missing:
        raise AssertionError(f"Clause omission — missing from summary: {missing}")

    # Rule 2: clause 5.2 must retain BOTH approvers.
    lower = summary_text.lower()
    if "5.2" in all_ids:
        if "department head" not in lower or "hr director" not in lower:
            raise AssertionError("Condition drop — clause 5.2 lost one of its two required approvers.")

    # Rule 3: no banned scope-bleed phrase introduced.
    hits = [p for p in BANNED_PHRASES if p in lower]
    if hits:
        raise AssertionError(f"Scope bleed — invented phrasing present: {hits}")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text, all_ids, multi_ids = summarize_policy(sections)
    _enforce(sections, summary_text, all_ids)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary_text)

    print(f"Done. Summary written to {args.output}")
    print(f"Clauses summarized: {len(all_ids)} "
          f"(across {len(sections)} sections)")
    print(f"Multi-condition clauses flagged: {len(multi_ids)} -> {', '.join(multi_ids)}")
    print("Enforcement checks passed: completeness, 5.2 dual-approver, no scope bleed.")


if __name__ == "__main__":
    main()
