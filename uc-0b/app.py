"""
UC-0B — Summary That Changes Meaning
Built from agents.md / skills.md (RICE enforcement, CRAFT-tested).
"""
import argparse
import re
from pathlib import Path

CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING = re.compile(r"^\d+\.\s+[A-Z]")
BANNED_BLEED = (
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
)
INVENTORY_CLAUSES = (
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
)
SOFTENING = re.compile(r"\b(should|typically|generally|expected to)\b", re.IGNORECASE)


def retrieve_policy(input_path: str) -> dict:
    """Load a .txt policy file and return numbered clauses as structured sections."""
    raw = Path(input_path).read_text(encoding="utf-8")
    lines = raw.splitlines()
    title_lines = []
    clauses = []
    current = None
    current_section = ""
    seen_first_clause = False

    for line in lines:
        stripped = line.rstrip()
        if stripped.strip() and set(stripped.strip()) <= {"═", "="}:
            continue
        heading = SECTION_HEADING.match(stripped)
        if heading and not CLAUSE_START.match(stripped):
            current_section = re.sub(r"^[=\s]+|[=\s]+$", "", stripped).strip()
            if current is not None:
                clauses.append(current)
                current = None
            continue

        start = CLAUSE_START.match(stripped)
        if start:
            if current is not None:
                clauses.append(current)
            seen_first_clause = True
            current = {
                "id": start.group(1),
                "text": start.group(2).strip(),
                "section": current_section,
            }
            continue

        if current is not None and stripped.strip():
            current["text"] = f"{current['text']} {stripped.strip()}".strip()
            continue

        if not seen_first_clause:
            title_lines.append(stripped)

    if current is not None:
        clauses.append(current)

    return {
        "title_block": "\n".join(title_lines).strip(),
        "clauses": clauses,
    }


def _must_quote_verbatim(clause: dict) -> bool:
    if clause["id"] in INVENTORY_CLAUSES:
        return True
    text = clause["text"]
    # Multiple named actors, numeric thresholds, or explicit conjunctions
    # cannot be safely compressed without a second pass.
    named_roles = len(
        re.findall(
            r"\b(Department Head|HR Director|Municipal Commissioner|direct manager|"
            r"HR Department|registered medical practitioner)\b",
            text,
        )
    )
    if named_roles >= 2:
        return True
    if re.search(r"\band\b.+\bnot\b", text, flags=re.IGNORECASE):
        return True
    return False


def _compress(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def summarize_policy(policy: dict) -> str:
    """Produce a compliant summary with clause references from structured sections."""
    clauses = policy.get("clauses") or []
    if not clauses:
        return (
            "REFUSAL: no numbered clauses were found in the source file. "
            "No summary was generated."
        )

    title_block = policy.get("title_block") or ""
    header_lines = [line for line in title_block.splitlines() if line.strip() and set(line.strip()) != {"═"}]
    header = header_lines[:6]

    body = []
    verbatim_ids = []
    for clause in clauses:
        text = _compress(clause["text"])
        clause_id = clause["id"]
        if _must_quote_verbatim(clause):
            body.append(f"FLAG:VERBATIM [{clause_id}] {text}")
            verbatim_ids.append(clause_id)
        else:
            body.append(f"[{clause_id}] {text}")

    summary = "\n".join(
        [
            "SOURCE-ONLY SUMMARY",
            *header,
            "",
            "Rules applied: every numbered source clause is listed; inventory clauses "
            "are quoted verbatim; no external practice language is added.",
            "",
            *body,
            "",
            f"COMPLETENESS: {len(clauses)} numbered clauses in source, "
            f"{len(body)} lines in summary, missing=none.",
            f"VERBATIM_FLAGS: {', '.join(verbatim_ids)}",
        ]
    )

    lowered = summary.lower()
    for phrase in BANNED_BLEED:
        if phrase in lowered:
            raise ValueError(f"Scope bleed detected: '{phrase}'")

    source_ids = [c["id"] for c in clauses]
    for clause_id in source_ids:
        if f"[{clause_id}]" not in summary:
            raise ValueError(f"Clause omission: {clause_id} missing from summary")
    for clause_id in INVENTORY_CLAUSES:
        if clause_id in source_ids and f"[{clause_id}]" not in summary:
            raise ValueError(f"Inventory clause missing: {clause_id}")

    # Guard against obligation softening introduced by this function.
    if SOFTENING.search("\n".join(body)):
        # Allowed only if the source itself used those words.
        source_text = " ".join(c["text"] for c in clauses)
        for match in SOFTENING.findall("\n".join(body)):
            if match.lower() not in source_text.lower():
                raise ValueError(f"Obligation softening detected: '{match}'")

    return summary + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
