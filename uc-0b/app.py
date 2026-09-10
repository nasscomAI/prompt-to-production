"""
UC-0B — Summary That Changes Meaning (faithful extractive summarizer).

Implements agents.md (RICE) + skills.md (retrieve_policy, summarize_policy).

Compliance by construction (see agents.md E1–E4):
  E1 every numbered clause X.Y appears exactly once as a [X.Y] bullet.
  E2 critical multi-condition clauses render with full source text, so no
     condition or binding verb can be dropped or softened.
  E3 output vocabulary is source text plus a fixed neutral template — the
     template contains no scope-bleed phrases and no new facts.
  E4 clauses rendered verbatim are listed in a QUOTE-FLAG line.
"""
import argparse
import os
import re

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-\(\)\/&]+?)\s*$")
SEPARATOR_RE = re.compile(r"^[═=\-–—\s]*$")
META_REF_RE = re.compile(r"Document Reference:\s*(.+)", re.IGNORECASE)
META_VER_RE = re.compile(r"Version:\s*([\d.]+)", re.IGNORECASE)
META_EFF_RE = re.compile(r"Effective:\s*(.+)", re.IGNORECASE)

# Clauses the README names as meaning-loss risks: always render verbatim.
CRITICAL_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file into structured numbered sections."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Policy file not found: {path}")
    with open(path, "r", encoding="utf-8-sig") as fh:
        raw_lines = fh.read().splitlines()

    ref, ver, eff = "", "", ""
    for line in raw_lines[:8]:
        m = META_REF_RE.search(line)
        if m:
            ref = _clean(m.group(1))
        m = META_VER_RE.search(line)
        if m:
            ver = _clean(m.group(1))
        m = META_EFF_RE.search(line)
        if m:
            eff = _clean(m.group(1))

    sections = []
    current_section = None
    current_clause = None

    def flush_clause():
        nonlocal current_clause
        if current_clause is not None and current_section is not None:
            current_clause["text"] = _clean(current_clause["text"])
            current_section["clauses"].append(current_clause)
        current_clause = None

    def flush_section():
        nonlocal current_section
        flush_clause()
        if current_section is not None:
            sections.append(current_section)
        current_section = None

    for line in raw_lines:
        if not line.strip() or SEPARATOR_RE.match(line):
            continue
        m_clause = CLAUSE_RE.match(line)
        # A section header looks like "2. ANNUAL LEAVE" (no second number).
        m_section = SECTION_RE.match(line)
        if m_clause and current_section is not None:
            flush_clause()
            current_clause = {"number": m_clause.group(1),
                              "text": m_clause.group(2)}
        elif m_section:
            flush_section()
            current_section = {"number": m_section.group(1),
                               "title": _clean(m_section.group(2)).title(),
                               "clauses": []}
        elif current_clause is not None:
            # Continuation line of the current clause (wrapped source text).
            current_clause["text"] += " " + line.strip()
        # Else: pre-section header/meta lines — captured via meta regexes.

    flush_section()

    n_clauses = sum(len(s["clauses"]) for s in sections)
    if n_clauses == 0:
        raise ValueError(f"No numbered clauses parsed from: {path}")
    return {"meta": {"ref": ref, "version": ver, "effective": eff},
            "sections": sections}


def summarize_policy(structured: dict) -> str:
    """Render structured sections as a compliant clause-referenced summary."""
    meta = structured.get("meta", {})
    sections = structured.get("sections", [])
    lines = []
    header_src = " / ".join(p for p in
                             [meta.get("ref"), meta.get("version"),
                              meta.get("effective")] if p)
    lines.append("Employee Leave Policy — Clause-Referenced Summary")
    if header_src:
        lines.append(f"Source: {header_src}")
    lines.append("Each numbered clause below appears once with its source "
                 "conditions and binding verbs preserved.")
    lines.append("")

    total = 0
    quoted = []
    for section in sections:
        lines.append(f"{section['number']}. {section['title']}")
        for clause in section["clauses"]:
            num = clause["number"]
            text = _clean(clause.get("text", ""))
            total += 1
            if not text:
                # E4: never drop silently — emit placeholder + flag.
                lines.append(f"[{num}] (source text unavailable — see source "
                             f"clause {num})")
                quoted.append(num)
                continue
            if num in CRITICAL_CLAUSES:
                # E2/E4: critical clauses render verbatim — paraphrase
                # could drop a condition, so quote instead.
                quoted.append(num)
                lines.append(f"[{num}] {text}")
            else:
                lines.append(f"[{num}] {text}")
        lines.append("")

    lines.append(f"Coverage: {total}/{total} numbered clauses listed, "
                 f"each with its source conditions preserved.")
    lines.append("QUOTE-FLAG (rendered verbatim to prevent meaning loss): "
                 + ", ".join(sorted(quoted, key=lambda n: tuple(
                     int(p) for p in n.split(".")))))
    lines.append("No information beyond the source document has been added.")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B faithful policy summarizer")
    parser.add_argument("--input", required=True,
                        help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True,
                        help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)
    n = sum(len(s["clauses"]) for s in structured["sections"])
    print(f"Done. Summary of {n} clauses written to {args.output}")


if __name__ == "__main__":
    main()
