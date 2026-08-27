"""
UC-0B — Summary That Changes Meaning
Implements agents.md + skills.md: retrieve_policy, summarize_policy.

Produces a clause-traceable summary: each agents.md clause_inventory id is present
via verbatim extraction from the source (no LLM required; no scope bleed).
"""
import argparse
import os
import re
import sys
from typing import Any, Dict, List, Optional

# --- agents.md clause_inventory (10 ground-truth clauses) ---
CLAUSE_INVENTORY: List[str] = [
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
]


def retrieve_policy(path: str) -> Dict[str, Any]:
    """
    skills.md retrieve_policy: load policy .txt, return raw_text + structured numbered sections.
    """
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(f"Policy file not found: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            raw_text = f.read()
    except OSError as e:
        raise OSError(f"Cannot read policy file: {path}") from e
    if not raw_text.strip():
        raise ValueError("Policy file is empty")

    sections = _parse_numbered_sections(raw_text)
    return {"raw_text": raw_text, "sections": sections}


def _parse_numbered_sections(text: str) -> List[Dict[str, str]]:
    """
    Split policy into blocks for sub-clauses X.Y at line start.
    Skips decorative box lines and major section banners (e.g. "3. SICK LEAVE") between clauses.
    """
    lines = text.splitlines()
    clause_start = re.compile(r"^(\d+\.\d+)\s")
    # "2. ANNUAL LEAVE" — single digit after dot, then space and letter (not 2.3 style)
    major_banner = re.compile(r"^\s*\d+\.\s+[A-Za-z]")
    box_line = re.compile(r"^[═\-\s]+$")

    sections: List[Dict[str, str]] = []
    i = 0
    while i < len(lines):
        m = clause_start.match(lines[i].strip())
        if not m:
            i += 1
            continue
        cid = m.group(1)
        body_lines = [lines[i]]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if clause_start.match(nxt.strip()):
                break
            ns = nxt.strip()
            if not ns:
                body_lines.append(lines[i])
                i += 1
                continue
            if box_line.match(ns):
                i += 1
                continue
            if major_banner.match(ns) and not clause_start.match(ns):
                i += 1
                continue
            body_lines.append(lines[i])
            i += 1
        sections.append({"clause_id": cid, "text": "\n".join(body_lines).strip()})
    return sections


def _section_text_by_id(sections: List[Dict[str, str]], clause_id: str) -> Optional[str]:
    for s in sections:
        if s.get("clause_id") == clause_id:
            return s["text"]
    return None


def _strip_clause_id_prefix(clause_id: str, text: str) -> str:
    """Avoid duplicate '2.3' when line already prefixed with [2.3]."""
    t = text.strip()
    pat = re.compile(r"^" + re.escape(clause_id) + r"\s+", re.M)
    return pat.sub("", t, count=1).strip()


def summarize_policy(
    retrieved: Dict[str, Any],
    inventory: Optional[List[str]] = None,
) -> str:
    """
    skills.md summarize_policy: structured sections → compliant summary with clause references.
    Uses extractive verbatim blocks for inventory clauses so obligations and binding verbs stay intact.
    """
    inv = inventory if inventory is not None else CLAUSE_INVENTORY
    sections: List[Dict[str, str]] = retrieved["sections"]
    missing = [c for c in inv if _section_text_by_id(sections, c) is None]
    if missing:
        # Fallback: scan raw text for missing ids (parsing edge cases)
        raw = retrieved["raw_text"]
        recovered: Dict[str, str] = {}
        for cid in missing:
            block = _extract_clause_block(raw, cid)
            if block:
                recovered[cid] = block
        if len(recovered) < len(missing):
            still = [c for c in missing if c not in recovered]
            raise ValueError(
                "summarize_policy: could not locate clauses in source: {!r}".format(still)
            )
        for cid, txt in recovered.items():
            sections.append({"clause_id": cid, "text": txt})

    lines_out: List[str] = [
        "UC-0B — HR Leave Policy summary (clause-traceable; extractive from source only)",
        "=" * 72,
        "",
        "Each item below maps to agents.md clause_inventory. Wording is taken from the policy text.",
        "",
    ]
    for cid in inv:
        text = _section_text_by_id(sections, cid)
        if not text:
            text = _extract_clause_block(retrieved["raw_text"], cid)
        if not text:
            raise ValueError(f"Clause {cid} not found in structured sections or raw text")
        body = _strip_clause_id_prefix(cid, text)
        compact = " ".join(body.split())
        lines_out.append(f"[{cid}] {compact}")
        lines_out.append("")
    lines_out.append(
        "End of summary — verify all 10 clause ids appear; clause 5.2 retains both approvers."
    )
    return "\n".join(lines_out).rstrip() + "\n"


def _extract_clause_block(raw: str, clause_id: str) -> Optional[str]:
    """Extract paragraph starting at clause_id when section list failed."""
    # Match clause_id at line start; capture until next line-start clause or end
    pattern = re.compile(
        r"(?ms)^(?P<body>" + re.escape(clause_id) + r"\s.+?)(?=^\d+\.\d+\s|\Z)"
    )
    m = pattern.search(raw)
    if m:
        return m.group("body").strip()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B: compliant clause-traceable policy summary (agents.md / skills.md)"
    )
    parser.add_argument(
        "--input",
        "-i",
        default=os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "policy-documents",
            "policy_hr_leave.txt",
        ),
        help="Path to policy .txt (default: ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=os.path.join(os.path.dirname(__file__), "summary_hr_leave.txt"),
        help="Path for summary output (default: uc-0b/summary_hr_leave.txt)",
    )
    args = parser.parse_args()
    input_path = os.path.normpath(args.input)
    output_path = os.path.normpath(args.output)

    try:
        retrieved = retrieve_policy(input_path)
        summary = summarize_policy(retrieved)
    except (FileNotFoundError, ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print("Wrote {} chars -> {}".format(len(summary), output_path))


if __name__ == "__main__":
    main()
