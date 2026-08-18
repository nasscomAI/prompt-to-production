"""
UC-0B app.py — Faithful HR leave-policy summariser.
Built from agents.md (RICE) + skills.md: retrieve_policy, summarize_policy.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ground-truth binding clauses from agents.md / README clause inventory.
REQUIRED_BINDING_CLAUSES = (
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

# Tokens that must survive in the summary for each binding clause
# (blocks clause omission and condition drop).
CLAUSE_MUST_RETAIN: Dict[str, Tuple[str, ...]] = {
    "2.3": ("must", "14", "HR-L1"),
    "2.4": ("must", "written", "Verbal"),
    "2.5": ("will", "LOP", "regardless"),
    "2.6": ("5", "forfeited", "31 December"),
    "2.7": ("must", "January", "March", "forfeited"),
    "3.2": ("requires", "3", "48"),
    "3.4": ("requires", "regardless"),
    "5.2": ("requires", "Department Head", "HR Director"),
    "5.3": ("requires", "30", "Municipal Commissioner"),
    "7.2": ("not permitted", "during service"),
}

SCOPE_BLEED_PHRASES = (
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "it is common practice",
    "generally understood",
    "best practice",
)

CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 /()&,-]+)$")
RULE_LINE = re.compile(r"^═+$")


class PolicyError(Exception):
    """Refusal / validation error — do not invent policy content."""


def retrieve_policy(input_path: str) -> List[Dict[str, str]]:
    """
    Skill: retrieve_policy
    Load a .txt policy file and return structured numbered sections.
    No paraphrasing.
    """
    path = Path(input_path)
    if not path.exists():
        raise PolicyError(f"Input file not found: {input_path}")
    if not path.is_file():
        raise PolicyError(f"Input path is not a file: {input_path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"Unable to read policy file: {exc}") from exc

    if not raw.strip():
        raise PolicyError("Policy file is empty — refuse to summarise.")

    sections: List[Dict[str, str]] = []
    current_heading = ""
    current_id: Optional[str] = None
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id is None:
            return
        text = " ".join(line.strip() for line in current_lines if line.strip())
        text = re.sub(r"\s+", " ", text).strip()
        sections.append(
            {
                "id": current_id,
                "heading": current_heading,
                "text": text,
            }
        )
        current_id = None
        current_lines = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or RULE_LINE.match(stripped):
            continue

        heading_match = SECTION_HEADING.match(stripped)
        if heading_match and not CLAUSE_START.match(stripped):
            flush()
            current_heading = f"{heading_match.group(1)}. {heading_match.group(2).strip()}"
            continue

        clause_match = CLAUSE_START.match(stripped)
        if clause_match:
            flush()
            current_id = clause_match.group(1)
            current_lines = [clause_match.group(2).strip()]
            continue

        if current_id is not None:
            current_lines.append(stripped)

    flush()

    if not sections:
        raise PolicyError(
            "No numbered clauses found — not a CMC leave policy with numbered "
            "clauses. Refuse to summarise; do not invent content."
        )

    return sections


def _contains_scope_bleed(text: str) -> Optional[str]:
    lower = text.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in lower:
            return phrase
    return None


def _preserves_required_tokens(clause_id: str, summary_line: str) -> bool:
    tokens = CLAUSE_MUST_RETAIN.get(clause_id)
    if not tokens:
        return True
    return all(token in summary_line for token in tokens)


def _summarise_clause(clause: Dict[str, str]) -> str:
    """
    Produce a faithful one-line summary. Prefer collapsed source text so
    binding verbs and multi-conditions are never invented or dropped.
    If meaning would be at risk for a binding clause (missing required
    tokens after any rewrite), quote verbatim and flag.
    """
    clause_id = clause["id"]
    source = clause["text"]
    collapsed = re.sub(r"\s+", " ", source).strip()

    # Controlled condensation: source-only, no added language.
    candidate = f"{clause_id}: {collapsed}"

    bleed = _contains_scope_bleed(candidate)
    if bleed:
        raise PolicyError(
            f"Scope bleed detected in draft for clause {clause_id}: '{bleed}'. "
            "Never add information not present in the source."
        )

    if clause_id in REQUIRED_BINDING_CLAUSES and not _preserves_required_tokens(
        clause_id, candidate
    ):
        return (
            f"{clause_id}: \"{collapsed}\" "
            f"[VERBATIM — meaning loss risk]"
        )

    # Multi-condition obligations (e.g. 5.2 dual approvers): if both
    # conditions are not clearly present, force verbatim flag.
    if clause_id == "5.2":
        if "Department Head" not in candidate or "HR Director" not in candidate:
            return (
                f"{clause_id}: \"{collapsed}\" "
                f"[VERBATIM — meaning loss risk]"
            )

    return candidate


def summarize_policy(sections: List[Dict[str, str]]) -> str:
    """
    Skill: summarize_policy
    Structured sections → compliant summary with clause references.
    """
    by_id = {s["id"]: s for s in sections}
    missing = [cid for cid in REQUIRED_BINDING_CLAUSES if cid not in by_id]
    if missing:
        raise PolicyError(
            "Clause omission — refuse complete summary. Missing required "
            f"binding clause(s): {', '.join(missing)}"
        )

    lines: List[str] = [
        "CITY MUNICIPAL CORPORATION — Employee Leave Policy Summary",
        "Source: HR-POL-001 (policy_hr_leave.txt) only — no external practice added.",
        "",
    ]

    last_heading = None
    for clause in sections:
        heading = clause.get("heading") or ""
        if heading and heading != last_heading:
            lines.append(heading)
            last_heading = heading

        summary_line = _summarise_clause(clause)

        # Obligation softening check: do not introduce hedges absent from source.
        soft_introductions = ("generally", "typically", "usually", "should probably")
        source_lower = clause["text"].lower()
        for soft in soft_introductions:
            if soft in summary_line.lower() and soft not in source_lower:
                raise PolicyError(
                    f"Obligation softening blocked for clause {clause['id']}: "
                    f"introduced '{soft}' not present in source."
                )

        if not _preserves_required_tokens(clause["id"], summary_line):
            # Final guard for binding clauses.
            collapsed = re.sub(r"\s+", " ", clause["text"]).strip()
            summary_line = (
                f"{clause['id']}: \"{collapsed}\" "
                f"[VERBATIM — meaning loss risk]"
            )

        lines.append(summary_line)

    # Final inventory check on full document text.
    full = "\n".join(lines)
    for cid in REQUIRED_BINDING_CLAUSES:
        if not re.search(rf"\b{re.escape(cid)}\b", full):
            raise PolicyError(
                f"Clause omission after summarise: {cid} missing from output."
            )
        if not _preserves_required_tokens(cid, full):
            raise PolicyError(
                f"Condition drop / softening detected for clause {cid}: "
                f"required tokens {CLAUSE_MUST_RETAIN[cid]} not all present."
            )

    bleed = _contains_scope_bleed(full)
    if bleed:
        raise PolicyError(f"Scope bleed in final summary: '{bleed}'.")

    return full + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarise HR leave policy without changing meaning."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy .txt (e.g. ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary (e.g. summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
    except PolicyError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)
    out_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {out_path}")
    print(
        f"Verified {len(REQUIRED_BINDING_CLAUSES)} binding clauses present "
        "with required conditions retained."
    )


if __name__ == "__main__":
    main()
