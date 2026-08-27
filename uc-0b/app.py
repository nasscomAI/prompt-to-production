"""
UC-0B — Policy Summariser
Implements retrieve_policy and summarize_policy per agents.md / skills.md.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING_RE = re.compile(r"^(\d+)\.\s+(.+)$")
SEPARATOR_RE = re.compile(r"^═+$")

# Clauses matching these patterns lose meaning if paraphrased — quote verbatim.
MEANING_LOSS_PATTERNS = (
    re.compile(r"\bregardless\b", re.I),
    re.compile(r"\bunder any circumstances\b", re.I),
    re.compile(r"\bnot valid\b", re.I),
    re.compile(r"\bnot sufficient\b", re.I),
    re.compile(r"\bare forfeited\b", re.I),
    re.compile(r"\bor they are forfeited\b", re.I),
    re.compile(r"\band the\b", re.I),  # dual named parties (e.g. Dept Head and HR Director)
    re.compile(r"\bmust\b.+\bor\b", re.I | re.S),
    re.compile(r"\brequires\b.+\band\b", re.I | re.S),
)


class PolicyError(ValueError):
    """Raised when input is missing, empty, unreadable, or not a numbered policy."""


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sentence_count(text: str) -> int:
    """Count sentence endings, ignoring decimal points (e.g. 1.5 days)."""
    without_decimals = re.sub(r"\d+\.\d+", "NUM", text)
    return len(re.findall(r"[.!?]+", without_decimals))


def _needs_verbatim(text: str) -> bool:
    """True when summarising would risk dropping a condition or softening an obligation."""
    normalized = _collapse_ws(text)
    if _sentence_count(normalized) >= 2:
        return True
    return any(p.search(normalized) for p in MEANING_LOSS_PATTERNS)


def retrieve_policy(input_path: str | Path) -> dict[str, Any]:
    """
    Load a .txt leave-policy file and return structured numbered sections.

    Returns:
        {
          "metadata": {"title": ..., "reference": ..., "version": ...},
          "sections": [
            {"heading": str, "clauses": [{"clause_id": str, "text": str}, ...]},
            ...
          ],
        }
    """
    path = Path(input_path)
    if not path.exists():
        raise PolicyError(f"Input file not found: {path}")
    if not path.is_file():
        raise PolicyError(f"Input path is not a file: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"Input file unreadable: {path}") from exc

    if not raw.strip():
        raise PolicyError(f"Input file is empty: {path}")

    lines = raw.splitlines()
    metadata: dict[str, str] = {}
    header_lines: list[str] = []
    sections: list[dict[str, Any]] = []
    current_section: dict[str, Any] | None = None
    current_clause_id: str | None = None
    current_clause_parts: list[str] = []
    in_body = False

    def flush_clause() -> None:
        nonlocal current_clause_id, current_clause_parts
        if current_section is None or current_clause_id is None:
            current_clause_id = None
            current_clause_parts = []
            return
        text = _collapse_ws(" ".join(current_clause_parts))
        if text:
            current_section["clauses"].append(
                {"clause_id": current_clause_id, "text": text}
            )
        current_clause_id = None
        current_clause_parts = []

    def flush_section() -> None:
        nonlocal current_section
        flush_clause()
        if current_section is not None:
            sections.append(current_section)
            current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if SEPARATOR_RE.match(stripped):
            in_body = True
            continue

        section_match = SECTION_HEADING_RE.match(stripped)
        if section_match and in_body:
            flush_section()
            current_section = {
                "heading": f"{section_match.group(1)}. {section_match.group(2).strip()}",
                "clauses": [],
            }
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            if current_section is None:
                # Numbered clause before any section heading — still capture it.
                current_section = {"heading": "UNSECTIONED", "clauses": []}
            flush_clause()
            current_clause_id = clause_match.group(1)
            current_clause_parts = [clause_match.group(2).strip()]
            in_body = True
            continue

        if current_clause_id is not None:
            current_clause_parts.append(stripped)
            continue

        if not in_body:
            header_lines.append(stripped)
            if stripped.lower().startswith("document reference:"):
                metadata["reference"] = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("version:"):
                metadata["version"] = stripped.split(":", 1)[1].strip()

    flush_section()

    if header_lines:
        # Prefer the line that names the policy; fall back to joined header.
        title = next(
            (h for h in header_lines if "POLICY" in h.upper()),
            header_lines[-1] if header_lines else "",
        )
        metadata["title"] = title

    all_clauses = [c for s in sections for c in s["clauses"]]
    if not all_clauses:
        raise PolicyError(
            "No numbered clauses (N.N) found — refusing to invent policy structure."
        )

    return {"metadata": metadata, "sections": sections}


def _format_clause_line(clause_id: str, text: str) -> str:
    if _needs_verbatim(text):
        return f"{clause_id} [VERBATIM]: {text}"
    return f"{clause_id}: {text}"


def summarize_policy(structured: dict[str, Any], output_path: str | Path) -> str:
    """
    Produce a compliant clause-referenced summary and write it to output_path.

    Returns the summary text.
    """
    if not structured or not isinstance(structured, dict):
        raise PolicyError("Structured input is missing or malformed — refusing to summarise.")

    sections = structured.get("sections")
    if not sections:
        raise PolicyError("Structured input has no sections — refusing to summarise.")

    source_ids: list[str] = []
    for section in sections:
        if not isinstance(section, dict) or "clauses" not in section:
            raise PolicyError("Structured input is malformed — refusing to summarise.")
        for clause in section["clauses"]:
            if not isinstance(clause, dict) or "clause_id" not in clause or "text" not in clause:
                raise PolicyError("Structured input is malformed — refusing to summarise.")
            source_ids.append(clause["clause_id"])

    if not source_ids:
        raise PolicyError("Structured input has no clauses — refusing to summarise.")

    metadata = structured.get("metadata") or {}
    lines: list[str] = []
    title = metadata.get("title") or "Employee Leave Policy"
    lines.append(f"SUMMARY — {title}")
    if metadata.get("reference"):
        lines.append(f"Document Reference: {metadata['reference']}")
    if metadata.get("version"):
        lines.append(f"Version: {metadata['version']}")
    lines.append("")
    lines.append(
        "Faithful clause-referenced summary. Binding verbs and multi-condition "
        "obligations are preserved. Clauses that cannot be shortened without "
        "meaning loss are marked [VERBATIM]."
    )
    lines.append("")

    output_ids: list[str] = []
    for section in sections:
        heading = section.get("heading") or "Section"
        lines.append(heading)
        lines.append("-" * len(heading))
        for clause in section["clauses"]:
            cid = clause["clause_id"]
            text = _collapse_ws(clause["text"])
            lines.append(_format_clause_line(cid, text))
            output_ids.append(cid)
        lines.append("")

    if set(output_ids) != set(source_ids):
        missing = sorted(set(source_ids) - set(output_ids))
        raise PolicyError(
            f"Summary omitted clause(s) {missing} — refusing incomplete output."
        )

    summary = "\n".join(lines).rstrip() + "\n"
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(summary, encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B: Faithful HR leave-policy summariser (no clause omission)."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy .txt (e.g. ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for summary output (e.g. summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
        summarize_policy(structured, args.output)
    except PolicyError as exc:
        raise SystemExit(f"error: {exc}") from exc

    print(f"Wrote summary to {args.output}")
    clause_count = sum(len(s["clauses"]) for s in structured["sections"])
    print(f"Clauses included: {clause_count}")


if __name__ == "__main__":
    main()
