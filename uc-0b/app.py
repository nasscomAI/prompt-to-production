"""
UC-0B — HR Policy Summarization Agent
======================================
Pure Python, no external dependencies, no API calls.

Skills:
  - retrieve_policy  : loads .txt policy file → structured numbered sections
  - summarize_policy : structured sections → compliant clause-preserving summary

Enforcement rules:
  1. Every numbered clause must be present in the summary.
  2. Multi-condition obligations must preserve ALL conditions.
  3. Never add information not present in the source document.
  4. If a clause cannot be summarised without meaning loss — quote verbatim and flag it.

Usage:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from pathlib import Path


# ===========================================================================
# SKILL 1 — retrieve_policy
# ===========================================================================

def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt HR policy file and return structured numbered sections.

    Returns:
        {
          "status"  : "ok" | "warning" | "error",
          "message" : str,
          "raw_text": str,
          "sections": [{"clause": "2.3", "text": "..."}, ...]
        }
    """
    path = Path(file_path)

    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}",
                "raw_text": "", "sections": []}

    try:
        raw_text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return {"status": "error", "message": f"Cannot read '{file_path}': {exc}",
                "raw_text": "", "sections": []}

    # Match lines that start a numbered clause e.g. "2.3", "Section 3.2"
    clause_header = re.compile(
        r"^[ \t]*(?:Section\s+)?(\d+\.\d+(?:\.\d+)*)\b", re.MULTILINE
    )

    matches = list(clause_header.finditer(raw_text))

    if not matches:
        return {
            "status": "warning",
            "message": "No numbered sections detected. Returning raw text — manual review required.",
            "raw_text": raw_text,
            "sections": [],
        }

    sections = []
    for i, m in enumerate(matches):
        clause_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        clause_text = raw_text[start:end].strip()
        # Strip leading colon/dash that sometimes follows the clause number
        clause_text = re.sub(r"^[\s:–\-]+", "", clause_text).strip()
        if clause_text:
            sections.append({"clause": clause_id, "text": clause_text})

    return {
        "status": "ok",
        "message": f"Parsed {len(sections)} clause(s).",
        "raw_text": raw_text,
        "sections": sections,
    }


# ===========================================================================
# SKILL 2 — summarize_policy
# ===========================================================================

# Keywords that signal multi-condition obligations
CONDITION_KEYWORDS = re.compile(
    r"\b(AND|OR|both|either|regardless|unless|except|nor)\b", re.IGNORECASE
)

# Matches "Title Case Role AND Another Role" patterns
ROLE_PATTERN = re.compile(
    r"[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*(?:\s+(?:AND|and)\s+[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)+"
)


def _is_complex(text: str) -> bool:
    return bool(CONDITION_KEYWORDS.search(text))


def _summarize_clause(clause_id: str, text: str) -> dict:
    """
    Produce a single-clause summary entry.

    Strategy:
    - Complex clauses (multi-condition language): reproduced verbatim and flagged.
    - Short simple clauses (≤ 120 chars): kept as-is (nothing to lose).
    - Long simple clauses: first sentence used as summary.
    """
    text_stripped = text.strip()
    flagged = False

    if _is_complex(text_stripped):
        # Preserve verbatim — multi-condition clauses are too risky to paraphrase
        summary = f"[VERBATIM – FLAGGED FOR REVIEW]\n{text_stripped}"
        flagged = True
    elif len(text_stripped) <= 120:
        summary = text_stripped
    else:
        # First sentence is typically the binding statement in policy documents
        summary = re.split(r"(?<=[.!?])\s+", text_stripped)[0]

    return {"clause": clause_id, "summary": summary, "flagged": flagged}


def _detect_condition_drops(sections: list, summary_items: list) -> list:
    """
    Post-processing guard: verify multi-role conditions from the source
    survived into the summary. Returns a list of warning strings.
    """
    warnings = []
    section_map = {s["clause"]: s["text"] for s in sections}

    for item in summary_items:
        clause_id = item["clause"]
        original = section_map.get(clause_id, "")
        summary_text = item["summary"]

        if not _is_complex(original):
            continue

        for match in ROLE_PATTERN.finditer(original):
            phrase = match.group(0)
            parts = re.split(r"\s+(?:AND|and)\s+", phrase)
            missing = [p for p in parts if p.lower() not in summary_text.lower()]
            if missing:
                warnings.append(
                    f"[CONDITION-DROP RISK] Clause {clause_id}: "
                    f"possible missing condition(s): {missing}. Manual review required."
                )
                item["flagged"] = True

    return warnings


def summarize_policy(retrieved: dict) -> dict:
    """
    Produce a compliant summary from the output of retrieve_policy.

    Returns:
        {
          "status"  : "ok" | "error",
          "message" : str,
          "summary" : [{"clause", "summary", "flagged"}, ...],
          "warnings": [...]
        }
    """
    if retrieved["status"] == "error":
        return {"status": "error", "message": retrieved["message"],
                "summary": [], "warnings": []}

    sections = retrieved.get("sections", [])

    if not sections:
        raw = retrieved.get("raw_text", "").strip()
        if not raw:
            return {"status": "error",
                    "message": "No sections and no raw text found.",
                    "summary": [], "warnings": []}
        return {
            "status": "ok",
            "message": "Warning: no numbered sections; raw text returned verbatim.",
            "summary": [{"clause": "N/A",
                          "summary": f"[VERBATIM – FLAGGED FOR REVIEW]\n{raw}",
                          "flagged": True}],
            "warnings": [retrieved.get("message", "")],
        }

    summary_items = [_summarize_clause(s["clause"], s["text"]) for s in sections]
    warnings = _detect_condition_drops(sections, summary_items)

    return {
        "status": "ok",
        "message": f"Summary produced for {len(summary_items)} clause(s).",
        "summary": summary_items,
        "warnings": warnings,
    }


# ===========================================================================
# OUTPUT WRITER
# ===========================================================================

def write_output(result: dict, output_path: str) -> None:
    """Write the summary to a human-readable text file."""
    lines = ["HR LEAVE POLICY — COMPLIANT SUMMARY", "=" * 60, ""]

    if result["status"] == "error":
        lines.append(f"ERROR: {result['message']}")
    else:
        for item in result["summary"]:
            flag_label = "  *** FLAGGED ***" if item.get("flagged") else ""
            lines.append(f"Clause {item['clause']}{flag_label}")
            lines.append("-" * 40)
            lines.append(item["summary"])
            lines.append("")

        if result.get("warnings"):
            lines += ["=" * 60, "WARNINGS", "=" * 60]
            for w in result["warnings"]:
                lines.append(f"  • {w}")
            lines.append("")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[app.py] Output written → {out}")


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarization Agent")
    parser.add_argument("--input",  required=True, help="Path to the .txt policy file.")
    parser.add_argument("--output", required=True, help="Path for the output summary file.")
    args = parser.parse_args()

    # Step 1 — load & parse
    print(f"[retrieve_policy] Loading: {args.input}")
    retrieved = retrieve_policy(args.input)
    print(f"[retrieve_policy] {retrieved['status'].upper()} — {retrieved['message']}")
    if retrieved["status"] == "ok" and retrieved["sections"]:
        print(f"[retrieve_policy] Clauses: {[s['clause'] for s in retrieved['sections']]}")

    if retrieved["status"] == "error":
        write_output({"status": "error", "message": retrieved["message"],
                      "summary": [], "warnings": []}, args.output)
        sys.exit(1)

    # Step 2 — summarize
    print("[summarize_policy] Building summary …")
    result = summarize_policy(retrieved)
    print(f"[summarize_policy] {result['status'].upper()} — {result['message']}")

    if result.get("warnings"):
        print("[summarize_policy] Warnings raised:")
        for w in result["warnings"]:
            print(f"  ⚠  {w}")

    # Step 3 — write
    write_output(result, args.output)


if __name__ == "__main__":
    main()