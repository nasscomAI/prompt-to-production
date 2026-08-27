"""
UC-0B app.py — Summary That Changes Meaning

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re


def retrieve_policy(path: str) -> dict:
    """Load the policy .txt and split into numbered clause sections."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    sections = {}
    # End markers: a new dotted clause (digit.digit ), a new top-level section
    # header (digit. SPACE, e.g. "3. SICK LEAVE"), or a divider line of '═'.
    end_re = re.compile(r"^\d+\.\d+\s+|^\d+\.\s+\S|^═+", re.MULTILINE)
    # Capture lines beginning with a dotted clause number (e.g. "2.4 ...")
    for match in re.finditer(r"^(\d+\.\d+)\s+(.*)$", text, re.MULTILINE):
        num = match.group(1)
        content = match.group(2).strip()
        start = match.end()
        nxt = end_re.search(text[start:])
        end = start + nxt.start() if nxt else len(text)
        block = (content + " " + text[start:end].strip()).strip()
        block = re.sub(r"\s+", " ", block)
        sections[num] = block
    return sections


def summarize_policy(sections: dict) -> str:
    """Produce a clause-faithful summary of the 10 target clauses."""
    target = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    lines = []
    lines.append("CMC HR LEAVE POLICY — CLAUSE-FAITHFUL SUMMARY")
    lines.append("(Source: policy_hr_leave.txt | HR-POL-001 v2.3)")
    lines.append("=" * 60)
    for num in target:
        raw = sections.get(num, "")
        if not raw:
            lines.append(f"{num}: [VERBATIM] <clause not found in source> [END VERBATIM]")
            continue
        lines.append(f"Clause {num}: {raw}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
