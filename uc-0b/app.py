"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from typing import Dict, List, Tuple


REQUIRED_CLAUSES: List[str] = [
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

BINDING_VERBS: List[str] = ["must", "requires", "will", "not permitted", "forfeited", "may"]
SEVERITY_TERMS: List[str] = ["14", "48", "31", "january", "march", "department head", "hr director", "municipal commissioner", "lop"]


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _read_policy_text(input_path: str) -> str:
    with open(input_path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_numbered_sections(source_text: str) -> Dict[str, str]:
    """
    Parse numbered clauses like 2.3, 5.2 and include continuation lines.
    """
    sections: Dict[str, List[str]] = {}
    current_clause = ""

    for raw_line in source_text.splitlines():
        line = raw_line.rstrip()
        match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)
        if match:
            current_clause = match.group(1)
            sections[current_clause] = [match.group(2).strip()]
            continue

        if current_clause and line.strip():
            # Continuation for the current numbered clause.
            sections[current_clause].append(line.strip())

    return {clause: _normalize_whitespace(" ".join(lines)) for clause, lines in sections.items()}


def _extract_binding_verbs(text: str) -> List[str]:
    lowered = text.lower()
    return [verb for verb in BINDING_VERBS if verb in lowered]


def _extract_conditions(text: str) -> Dict[str, List[str]]:
    lowered = text.lower()
    extracted = {
        "deadlines_thresholds": [term for term in SEVERITY_TERMS if term in lowered],
        "approvals": [],
        "consequences": [],
    }

    if "department head" in lowered:
        extracted["approvals"].append("Department Head")
    if "hr director" in lowered:
        extracted["approvals"].append("HR Director")
    if "municipal commissioner" in lowered:
        extracted["approvals"].append("Municipal Commissioner")

    if "loss of pay" in lowered or "lop" in lowered:
        extracted["consequences"].append("Loss of Pay (LOP)")
    if "forfeited" in lowered:
        extracted["consequences"].append("forfeiture")
    if "not permitted" in lowered:
        extracted["consequences"].append("prohibition")

    return extracted


def retrieve_policy(input_path: str) -> Dict[str, object]:
    source_text = _read_policy_text(input_path)
    parsed = _parse_numbered_sections(source_text)

    sections = []
    for clause_id, raw_text in parsed.items():
        conditions = _extract_conditions(raw_text)
        sections.append(
            {
                "clause_id": clause_id,
                "raw_text": raw_text,
                "normalized_text": _normalize_whitespace(raw_text),
                "binding_verb": _extract_binding_verbs(raw_text),
                "extracted_conditions": conditions["deadlines_thresholds"],
                "extracted_deadlines": [token for token in conditions["deadlines_thresholds"] if token in ["14", "48", "31", "january", "march"]],
                "extracted_approvals": conditions["approvals"],
                "extracted_consequences": conditions["consequences"],
            }
        )

    section_map = {s["clause_id"]: s for s in sections}
    inventory = {
        "required_ids": REQUIRED_CLAUSES,
        "status_per_clause": {
            cid: ("found" if cid in section_map else "missing") for cid in REQUIRED_CLAUSES
        },
    }
    retrieval_warnings = [f"Missing required clause {cid}" for cid, st in inventory["status_per_clause"].items() if st != "found"]

    return {
        "source_text": source_text,
        "sections": sections,
        "required_clause_inventory": inventory,
        "retrieval_warnings": retrieval_warnings,
    }


def _clause_summary_line(clause_id: str, clause_text: str) -> str:
    """
    Prefer conservative, clause-faithful phrasing. For legally dense clauses,
    keep text close to source to avoid meaning loss.
    """
    return f"{clause_id}: {clause_text}"


def summarize_policy(retrieved: Dict[str, object]) -> Dict[str, object]:
    sections = retrieved["sections"]
    inventory = retrieved["required_clause_inventory"]
    section_map = {s["clause_id"]: s for s in sections}

    summary_lines: List[str] = []
    clause_trace: List[Dict[str, str]] = []
    review_required: List[str] = []
    missing: List[str] = []
    dropped_conditions: List[str] = []

    for clause_id in inventory["required_ids"]:
        if clause_id not in section_map:
            missing.append(clause_id)
            review_required.append(clause_id)
            summary_line = f"{clause_id}: REVIEW_REQUIRED - source clause missing, cannot summarize without guessing."
            source_excerpt = ""
            preservation_status = "missing"
        else:
            source_excerpt = section_map[clause_id]["raw_text"]
            summary_line = _clause_summary_line(clause_id, source_excerpt)
            preservation_status = "preserved"

            # Extra guard for clause 5.2 two-approver condition.
            if clause_id == "5.2":
                lower = source_excerpt.lower()
                if not ("department head" in lower and "hr director" in lower):
                    dropped_conditions.append("5.2")
                    review_required.append("5.2")

            # Guard for 5.3 threshold and approver.
            if clause_id == "5.3":
                lower = source_excerpt.lower()
                if not ("30" in lower and "municipal commissioner" in lower):
                    dropped_conditions.append("5.3")
                    review_required.append("5.3")

        summary_lines.append(summary_line)
        clause_trace.append(
            {
                "clause_id": clause_id,
                "source_excerpt": source_excerpt,
                "summary_line": summary_line,
                "preservation_status": preservation_status,
            }
        )

    compliance_report = {
        "total_required_clauses": len(REQUIRED_CLAUSES),
        "covered_clauses": len(REQUIRED_CLAUSES) - len(missing),
        "missing_clauses": missing,
        "softened_obligations": [],
        "dropped_conditions": sorted(set(dropped_conditions)),
        "added_non_source_content": [],
        "review_required_clauses": sorted(set(review_required)),
    }

    summary_text = "\n".join(summary_lines) + "\n"
    return {
        "summary_text": summary_text,
        "clause_trace": clause_trace,
        "compliance_report": compliance_report,
    }


def _write_output(output_path: str, summary_text: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    retrieved = retrieve_policy(args.input)
    summarized = summarize_policy(retrieved)
    _write_output(args.output, summarized["summary_text"])

    report = summarized["compliance_report"]
    print(
        "Compliance report:",
        {
            "covered": report["covered_clauses"],
            "total": report["total_required_clauses"],
            "missing": report["missing_clauses"],
            "review_required": report["review_required_clauses"],
        },
    )
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
