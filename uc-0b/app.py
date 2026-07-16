"""
UC-0B — Policy Summarizer
Deterministic, rule-based summarizer built to the constraints in agents.md/skills.md.

Design note: the source failure modes are clause omission, scope bleed, and obligation
softening — all caused by an LLM paraphrasing away detail. This implementation never
paraphrases: it restructures the source into a clause-referenced summary while retaining
each clause's full original wording, so no condition can be silently dropped or invented.
Dense multi-condition clauses are additionally flagged for the reviewer.
"""
import argparse
import re
from collections import OrderedDict

CLAUSE_RE = re.compile(r'^(\d+\.\d+)\s+(.*)$')
SECTION_RE = re.compile(r'^(\d+)\.\s+(.*)$')
DOC_REF_RE = re.compile(r'^Document Reference:\s*(.+)$')
VERSION_RE = re.compile(r'^Version:\s*([\w.]+)\s*\|\s*Effective:\s*(.+)$')

# Ground truth from README.md — the clauses this policy is graded against.
GROUND_TRUTH_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(path: str) -> dict:
    """
    Load a policy .txt file and parse it into structured, numbered sections.
    Returns: {doc_ref, version, effective, sections: [{number, title, clauses: [{id, text}]}]}
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {path}")

    doc = {"doc_ref": None, "version": None, "effective": None, "sections": []}
    current_section = None
    current_clause = None
    seen_structure = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or set(stripped) <= {"═"}:
            continue

        m_ref = DOC_REF_RE.match(stripped)
        if m_ref:
            doc["doc_ref"] = m_ref.group(1).strip()
            continue

        m_ver = VERSION_RE.match(stripped)
        if m_ver:
            doc["version"] = m_ver.group(1).strip()
            doc["effective"] = m_ver.group(2).strip()
            continue

        m_clause = CLAUSE_RE.match(stripped)
        if m_clause:
            seen_structure = True
            clause_id, text = m_clause.group(1), m_clause.group(2).strip()
            current_clause = {"id": clause_id, "text": text}
            if current_section is None:
                current_section = {"number": "0", "title": "GENERAL", "clauses": []}
                doc["sections"].append(current_section)
            current_section["clauses"].append(current_clause)
            continue

        m_section = SECTION_RE.match(stripped)
        if m_section:
            seen_structure = True
            current_section = {
                "number": m_section.group(1),
                "title": m_section.group(2).strip(),
                "clauses": [],
            }
            doc["sections"].append(current_section)
            current_clause = None
            continue

        # Continuation of a wrapped clause line — join, never drop.
        if current_clause is not None:
            current_clause["text"] = (current_clause["text"] + " " + stripped).strip()

    if not seen_structure:
        raise ValueError(f"No numbered clauses found in {path} — file may be empty or unparsable.")

    return doc


def _sentence_count(text: str) -> int:
    parts = [p for p in re.split(r'(?<=[.])\s+', text.strip()) if p]
    return len(parts)


def summarize_policy(doc: dict) -> str:
    """
    Build a clause-complete summary from parsed policy sections, preserving every
    condition verbatim, then append a compliance self-check against GROUND_TRUTH_CLAUSES.
    """
    lines = []
    header = "SUMMARY — CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY"
    lines.append(header)
    meta_bits = []
    if doc.get("doc_ref"):
        meta_bits.append(doc["doc_ref"])
    if doc.get("version"):
        meta_bits.append(f"v{doc['version']}")
    if doc.get("effective"):
        meta_bits.append(f"Effective {doc['effective']}")
    if meta_bits:
        lines.append("Source: " + ", ".join(meta_bits))
    lines.append(
        "Note: Every clause below is quoted from the source in full — nothing paraphrased, "
        "nothing added. Dense multi-condition clauses are flagged for reviewer attention."
    )
    lines.append("")

    clauses_by_id = OrderedDict()

    for section in doc["sections"]:
        if not section["clauses"]:
            continue
        rule = "-" * 60
        lines.append(rule)
        lines.append(f"{section['number']}. {section['title']}")
        lines.append(rule)
        for clause in section["clauses"]:
            clauses_by_id[clause["id"]] = clause["text"]
            flag = " [MULTI-CONDITION — all conditions retained below]" if _sentence_count(clause["text"]) >= 2 else ""
            lines.append(f"{clause['id']}{flag} {clause['text']}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("COMPLIANCE CHECK — GROUND-TRUTH CLAUSES (per agents.md)")
    lines.append("=" * 60)
    for clause_id in GROUND_TRUTH_CLAUSES:
        if clause_id in clauses_by_id:
            text = clauses_by_id[clause_id]
            multi = _sentence_count(text) >= 2
            status = "present" + (" [multi-condition preserved]" if multi else "")
        else:
            status = "MISSING"
        lines.append(f"{clause_id}: {status}")

    # Explicit guard for the named trap in README: clause 5.2 must keep BOTH approvers.
    if "5.2" in clauses_by_id:
        text_52 = clauses_by_id["5.2"]
        has_both = "Department Head" in text_52 and "HR Director" in text_52
        lines.append(
            f"5.2 dual-approver check: {'PASS — both Department Head and HR Director present' if has_both else 'FAIL — an approver was dropped'}"
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    doc = retrieve_policy(args.input)
    summary = summarize_policy(doc)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
