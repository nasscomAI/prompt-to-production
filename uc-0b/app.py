"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

REQUIRED_CLAUSES = ["2.3","2.4","2.5","2.6","2.7","3.2","3.4","5.2","5.3","7.2"]


def load_clauses(text):
    # Find clause headings like '2.3 ' at line starts and capture until next clause
    pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$", re.MULTILINE)
    clauses = {}
    # naive paragraph split: split on lines that start with a clause number
    lines = text.splitlines()
    current = None
    buffer = []
    for line in lines:
        m = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if m:
            if current:
                clauses[current] = " ".join(buffer).strip()
            current = m.group(1)
            buffer = [m.group(2).strip()]
        elif re.match(r"^\d+\.\s+", line):
            if current:
                clauses[current] = " ".join(buffer).strip()
            current = None
            buffer = []
        else:
            if current:
                buffer.append(line.strip())
    if current:
        clauses[current] = " ".join(buffer).strip()
    return clauses


def make_summary(clauses):
    out_lines = []
    for c in REQUIRED_CLAUSES:
        text = clauses.get(c)
        if not text:
            raise ValueError(f"Required clause {c} is missing from the source policy")
        # If clause contains 'and' conditions or multiple approvers, prefer verbatim QUOTED
        # to avoid dropping conditions. For simplicity, if clause contains 'and' or 'AND' or
        # commas with 'and', we QUOTE it to be safe.
        if re.search(r"\bAND\b| and |, and | requires ", text, re.IGNORECASE):
            out_lines.append(f"{c}: QUOTED: {text}")
        else:
            out_lines.append(f"{c}: {text}")
    return "\n\n".join(out_lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    with open(args.input, encoding="utf-8") as f:
        txt = f.read()

    clauses = load_clauses(txt)
    summary = make_summary(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    main()
