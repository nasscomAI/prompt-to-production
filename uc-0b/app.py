"""
UC-0B app.py
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ==============================
# CONFIG
# ==============================

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

SECTION_TITLES = {
    "2": "Annual Leave",
    "3": "Sick Leave",
    "5": "Leave Without Pay",
    "7": "Leave Encashment",
}

VAGUE_PHRASES = [
    "typically", "generally", "usually", "standard practice"
]

MISSING = "[CLAUSE NOT FOUND IN DOCUMENT — manual verification required]"
RISK = "[VERBATIM — condition-drop risk]"

# FIX 2 & 3: Pattern that matches a genuine clause ID — must be at the start
# of a line (after stripping) or after a newline, so "Version: 2.3" and
# "1.5 days" in mid-sentence are excluded.
# A real clause looks like: "2.3 Some text" — digit.digit at start of a token
# after a newline, optionally with leading whitespace.
_CLAUSE_LINE_RE = re.compile(r"(?m)^[ \t]*(\d+\.\d+)\b")


class PolicyError(Exception):
    pass


# ==============================
# CLEAN RAW TEXT
# ==============================

def _clean_raw_text(text: str) -> str:
    lines = []

    for line in text.splitlines():
        s = line.strip()

        # Remove separators
        if re.match(r"^[=\-─═]{3,}$", s):
            continue

        # Remove section headers — only pure header lines like "2. ANNUAL LEAVE"
        # Tightened: must start with digit, optional dot, then only alpha+space to EOL.
        # Excludes lines with parens "(LWP)", pipes "|", colons ":", etc.
        if re.match(r"^\d+[\.\-]?\s+[A-Z][A-Z\s]+$", s):
            continue

        if not s:
            continue

        lines.append(line)

    return "\n".join(lines)


# ==============================
# NORMALIZATION
# ==============================

def _normalize(text: str) -> str:
    # Collapse line continuations (indented continuation lines join to previous)
    text = re.sub(r"\n[ \t]+", " ", text)

    # Normalize remaining whitespace within lines
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# ==============================
# EXTRACT CLAUSES 
# ==============================

def _extract(text: str) -> Dict[str, str]:
    """
    Extracts only genuine clause IDs — those that appear at the start of a line.
    This prevents decimal numbers in prose ("1.5 days", "Version: 2.3") from
    being mistaken for clause identifiers.
    """
    # Normalize first (collapses continuation lines, not all newlines)
    text = _normalize(text)

    # Find clause IDs only at line-start positions
    matches = list(_CLAUSE_LINE_RE.finditer(text))

    clauses = {}

    for i, match in enumerate(matches):
        clause_id = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        # FIX 1: Only strip leading punctuation/spaces — NOT trailing "."
        # Trailing periods are part of the sentence and must be preserved.
        body = text[start:end].strip(" :\t").rstrip()

        if body:
            clauses[clause_id] = body

    return clauses


def retrieve_policy(path: str) -> Dict[str, str]:
    file = Path(path)

    if not file.exists():
        raise PolicyError("File not found")

    raw = file.read_text(encoding="utf-8")

    if not raw.strip():
        raise PolicyError("Empty file")

    raw = _clean_raw_text(raw)

    extracted = _extract(raw)

    if not extracted:
        raise PolicyError("No clauses found")

    return {c: extracted.get(c, "") for c in REQUIRED_CLAUSES}


# ==============================
# VALIDATION
# ==============================

def _process_clause(cid: str, text: str) -> str:
    if not text:
        return MISSING

    # Normalize inline whitespace only — preserve sentence-ending periods
    text = re.sub(r"[ \t]+", " ", text).strip()

    if cid == "5.2":
        if not ("Department Head" in text and "HR Director" in text):
            return f"{text} {RISK}"

    return text


def _check_vague(text: str) -> Tuple[bool, List[str]]:
    found = [p for p in VAGUE_PHRASES if re.search(rf"\b{p}\b", text, re.IGNORECASE)]
    return len(found) == 0, found


# ==============================
# OUTPUT BUILDER 
# ==============================

def summarize_policy(clauses: Dict[str, str]) -> str:

    summaries = {c: _process_clause(c, clauses[c]) for c in REQUIRED_CLAUSES}

    sections: Dict[str, List[str]] = {}

    for c in REQUIRED_CLAUSES:
        sec = c.split(".")[0]
        sections.setdefault(sec, []).append(f"{c}: {summaries[c]}")

    lines = []

    # HEADER
    lines.append("# HR LEAVE POLICY — COMPLIANT SUMMARY")
    lines.append("")

    # SECTIONS (STRICT ORDER)
    for sec in ["2", "3", "5", "7"]:
        if sec not in sections:
            continue

        lines.append(f"Section {sec} — {SECTION_TITLES[sec]}")
        lines.append("")

        lines.extend(sections[sec])
        lines.append("")

    # OMISSION
    missing = [c for c, t in summaries.items() if t == MISSING]

    lines.append("Omission Report")
    lines.append("None." if not missing else f"Missing clauses: {', '.join(missing)}")
    lines.append("")

    # RISKS
    risks = []
    for c, t in summaries.items():
        if t == MISSING:
            risks.append(f"{c}: missing clause")
        if RISK in t:
            risks.append(f"{c}: missing dual approval")

    lines.append("Validation Risk Report")
    lines.append("None." if not risks else "\n".join(risks))
    lines.append("")

    # FINAL
    no_vague, _ = _check_vague("\n".join(lines))

    lines.append("Final Verification:")
    lines.append(f"- Required clauses checked: {len(REQUIRED_CLAUSES)}/{len(REQUIRED_CLAUSES)}")
    lines.append(f"- Missing clauses: {', '.join(missing) if missing else 'None'}")
    lines.append(
        f"- Clause 5.2 dual-approval validation: "
        f"{'PASS' if '5.2' not in [c for c, t in summaries.items() if RISK in t] else 'FAIL'}"
    )
    lines.append(f"- Vague phrase scan: {'PASS' if no_vague else 'FAIL'}")

    status = "PASS" if not missing and no_vague and not risks else "REVIEW REQUIRED"
    lines.append(f"- Overall compliance status: {status}")

    final = "\n".join(lines)

    if not no_vague:
        raise PolicyError("Vague phrases detected")

    return final


# ==============================
# CLI
# ==============================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        Path(args.output).write_text(summary, encoding="utf-8")

        print("[INFO] Summary generated successfully")

    except PolicyError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()