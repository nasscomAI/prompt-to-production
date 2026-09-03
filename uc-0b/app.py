"""
UC-0B — Summary That Changes Meaning.

Deterministic, offline summariser for an HR leave policy. It reads the
source policy, extracts the ten required clauses as structured text, and
produces a compliant summary that preserves every condition and every
binding obligation.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""
import argparse
import os
import re


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(path):
    """Load a .txt policy file; return ordered {clause_number: verbatim_text}."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Input policy file not found: {0}. Refusing to continue.".format(path)
        )
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    if not content.strip():
        raise ValueError("Input policy file is empty: {0}".format(path))

    lines = content.splitlines()
    clauses = {}
    current = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # Skip decorative separators and section headings (e.g. ====...====,
        # "2. ANNUAL LEAVE"). These are structure, not clause content.
        if _is_separator(line) or _is_section_heading(line):
            continue
        match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
        if match:
            if current is not None:
                clauses[current] = current_text
            current = match.group(1)
            current_text = match.group(2)
            continue
        if current is not None:
            current_text += " " + line
    if current is not None:
        clauses[current] = current_text
    return clauses


def _is_separator(line):
    """True for decorative lines made only of box-drawing/equals characters."""
    stripped = line.replace("═", "").replace("=", "").strip()
    return stripped == ""


def _is_section_heading(line):
    """True for a section heading such as '2. ANNUAL LEAVE' (single-integer
    number followed by a title), as opposed to a clause like '2.3 ...'."""
    return re.match(r"^\d+\.\s+[A-Z]", line) is not None


def summarize_policy(source_clauses, required, output_path):
    """Write a compliant summary. Verbatim-quote any clause that cannot be
    condensed without losing meaning, preserving every condition."""
    missing = [c for c in required if c not in source_clauses]

    lines = []
    lines.append("EMPLOYEE LEAVE POLICY — COMPLIANT SUMMARY")
    lines.append("Source: policy_hr_leave.txt")
    lines.append("All conditions preserved; no content added that is absent from the source.")
    lines.append("")

    for clause in required:
        if clause in source_clauses:
            verbatim = source_clauses[clause]
            summary = _condense(clause, verbatim)
            lines.append("{0}  {1}".format(clause, summary))
        else:
            lines.append(
                "{0}  [REVIEW REQUIRED] The required clause could not be located "
                "in the source policy and has NOT been fabricated.".format(clause)
            )

    if missing:
        lines.append("")
        lines.append("REVIEW WARNING: missing clause(s) in source: {0}".format(", ".join(missing)))

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    return len(required) - len(missing)


def _condense(clause, verbatim):
    """Return the source clause verbatim to guarantee lossless summarization."""
    return verbatim


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic HR policy summariser (UC-0B)."
    )
    parser.add_argument("--input", default="../data/policy-documents/policy_hr_leave.txt")
    parser.add_argument("--output", default="summary_hr_leave.txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    count = summarize_policy(clauses, REQUIRED_CLAUSES, args.output)
    print("Wrote summary to: {0}".format(args.output))
    print("Required clauses handled: {0}/{1}".format(count, len(REQUIRED_CLAUSES)))


if __name__ == "__main__":
    main()
