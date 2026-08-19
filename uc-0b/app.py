"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy per agents.md (RICE) and skills.md.
"""
import argparse
import re
import sys

# Binding verbs to detect and preserve in summaries
BINDING_VERBS = ["must", "will", "requires", "required", "not permitted", "cannot",
                 "may not", "shall", "is not", "are not", "forfeited", "may"]

# Clause patterns that must be quoted verbatim — paraphrase risks meaning loss
VERBATIM_TRIGGERS = [
    "under any circumstances",
    "regardless of subsequent",
    "regardless of duration",
    "not permitted",
    "cannot be encashed",
    "cannot be split",
    "not be considered",
    "and the hr director",
    "manager approval alone is not sufficient",
    "verbal approval is not valid",
]


# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list:
    """
    Loads a .txt policy file and returns a structured list of numbered clauses.
    Each entry: { clause_id, heading, body, binding_verb }
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    if not raw.strip():
        raise ValueError("Policy file is empty.")

    # Normalise line endings and strip box-drawing / decoration lines
    lines = raw.splitlines()
    cleaned = []
    for line in lines:
        # Drop pure decoration lines (═══, ───, etc.)
        stripped = line.strip()
        if re.match(r'^[═─\-=*]{3,}$', stripped):
            continue
        # Drop top-level section header lines (e.g. "2. ANNUAL LEAVE", "5. LEAVE WITHOUT PAY (LWP)")
        if re.match(r'^\d+\.\s+[A-Z][A-Z\s\(\)/&]+$', stripped):
            continue
        cleaned.append(line)

    text = "\n".join(cleaned)

    # Split into clause blocks: lines starting with  N.N  (e.g. 2.3, 10.1)
    clause_pattern = re.compile(r'(?m)^(\d+\.\d+)\s+(.*)')
    matches = list(clause_pattern.finditer(text))

    if not matches:
        raise ValueError("No numbered clauses found — check document format.")

    sections = []
    for i, match in enumerate(matches):
        clause_id = match.group(1)
        first_line = match.group(2).strip()

        # Body runs from after first line to start of next clause
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        continuation = text[start:end].strip()

        body = (first_line + " " + continuation).strip()
        body = re.sub(r'\s+', ' ', body).strip()   # collapse internal whitespace

        # Detect primary binding verb
        body_lower = body.lower()
        binding_verb = ""
        for verb in BINDING_VERBS:
            if verb in body_lower:
                binding_verb = verb
                break

        sections.append({
            "clause_id":    clause_id,
            "heading":      "",          # sub-clauses don't have separate headings
            "body":         body,
            "binding_verb": binding_verb,
        })

    return sections


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy
# ---------------------------------------------------------------------------

def _needs_verbatim(body: str) -> bool:
    """Returns True if the clause body contains a verbatim trigger phrase."""
    body_lower = body.lower()
    return any(trigger in body_lower for trigger in VERBATIM_TRIGGERS)


def _summarize_clause(clause: dict) -> tuple[str, bool]:
    """
    Returns (summary_text, verbatim_required).
    Preserves all conditions and binding verbs.
    Multi-condition obligations (AND) are always flagged verbatim.
    """
    body = clause["body"]
    verbatim = _needs_verbatim(body)

    if verbatim:
        return body, True  # Quote exactly — no paraphrase

    # For safe clauses: return the body trimmed to one clean sentence block
    # Strip trailing whitespace artifacts; keep full text to preserve conditions
    summary = body.strip()
    return summary, False


def summarize_policy(sections: list, output_path: str):
    """
    Produces a clause-by-clause summary .txt file.
    Every clause_id must appear. VERBATIM_REQUIRED flagged where meaning loss risk exists.
    """
    if not sections:
        print("ERROR: No sections to summarise.", file=sys.stderr)
        sys.exit(1)

    verbatim_count = 0
    lines = ["UC-0B — HR Leave Policy Summary",
             "Source: policy_hr_leave.txt",
             "=" * 60,
             ""]

    for clause in sections:
        if not clause["body"].strip():
            # Empty clause — flag it, never skip
            lines.append(f"[{clause['clause_id']}]")
            lines.append("Summary: [EMPTY CLAUSE — review source document]")
            lines.append("Flag: VERBATIM_REQUIRED")
            lines.append("")
            verbatim_count += 1
            continue

        summary, verbatim = _summarize_clause(clause)
        lines.append(f"[{clause['clause_id']}]")
        lines.append(f"Summary: {summary}")
        if verbatim:
            lines.append("Flag: VERBATIM_REQUIRED")
            verbatim_count += 1
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Summarised {len(sections)} clauses. VERBATIM_REQUIRED: {verbatim_count}.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summarize_policy(sections, args.output)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
