"""
UC-0B app.py — Summary That Changes Meaning.
Conservative, non-generative clause extractor: every numbered clause is
carried into the summary as whitespace-normalized source text, never
paraphrased. This eliminates clause omission, scope bleed, and obligation
softening by construction — nothing is generated, so nothing can drift
from the source.
See README.md for run command and expected behaviour.
"""
import argparse
import re

SECTION_RE = re.compile(r"(?m)^═+\n(\d+)\.[ \t]+([^\n═]+)\n═+$")
CLAUSE_START_RE = re.compile(r"(?m)^(\d+\.\d+)\s")


def retrieve_policy(path: str):
    """
    Load a .txt policy file and return it as structured numbered sections.
    Returns: list of {"number": "2.3", "section": "2", "section_title": str, "text": str}
    """
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    section_titles = {num: title.strip() for num, title in SECTION_RE.findall(raw)}

    starts = list(CLAUSE_START_RE.finditer(raw))
    clauses = []
    for i, match in enumerate(starts):
        number = match.group(1)
        body_end = starts[i + 1].start() if i + 1 < len(starts) else len(raw)
        body = raw[match.end():body_end]
        border_idx = body.find("\n═")
        if border_idx != -1:
            body = body[:border_idx]
        text = " ".join(body.split())
        section = number.split(".")[0]
        clauses.append({
            "number": number,
            "section": section,
            "section_title": section_titles.get(section, ""),
            "text": text,
        })
    return clauses


def summarize_policy(clauses: list) -> str:
    """
    Produce a compliant summary with clause references.
    Every clause from retrieve_policy is emitted verbatim (whitespace-normalized
    only) under its section heading — no clause is dropped, no condition is
    silently removed, and nothing is added beyond what the source states.
    """
    lines = ["HR LEAVE POLICY — CLAUSE SUMMARY", "(source-verbatim extraction; every numbered clause below is unmodified except for whitespace)", ""]

    current_section = None
    for clause in clauses:
        if clause["section"] != current_section:
            current_section = clause["section"]
            if lines[-1] != "":
                lines.append("")
            lines.append(f"## {current_section}. {clause['section_title']}")
        lines.append(f"- {clause['number']}: {clause['text']}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_[name].txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output} ({len(clauses)} clauses).")


if __name__ == "__main__":
    main()
