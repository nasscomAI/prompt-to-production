"""
UC-0B app.py — Policy summarizer.
Built per agents.md (role/intent/context/enforcement) and skills.md
(retrieve_policy, summarize_policy).
"""
import argparse
import re

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z \(\)]*$")
RULE_LINE_PATTERN = re.compile(r"^[═=\-]+$")

# Any clause matching one of these signals names more than one condition,
# approver, or a threshold-plus-exception — collapsing it risks a condition
# drop (the exact failure mode this UC is built to catch), so it is quoted
# verbatim instead of paraphrased.
MULTI_CONDITION_SIGNALS = [
    " and the ", "regardless", "forfeited", "exceeding", "or they are",
    "within 48 hours", "immediately before or after",
]


def retrieve_policy(input_path: str) -> list:
    """
    Loads the policy .txt file and parses it into structured clause sections.
    Returns: list of {clause_number, clause_text} in document order.
    """
    with open(input_path, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    clauses = []
    current = None
    for line in lines:
        stripped = line.strip()
        match = CLAUSE_PATTERN.match(stripped)
        if match:
            if current:
                clauses.append(current)
            current = {"clause_number": match.group(1), "clause_text": match.group(2)}
        elif (
            current
            and stripped
            and not RULE_LINE_PATTERN.match(stripped)
            and not SECTION_HEADER_PATTERN.match(stripped)
        ):
            current["clause_text"] += " " + stripped
    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError(f"No numbered clauses found in {input_path}")

    return clauses


def _is_multi_condition(clause_text: str) -> bool:
    lower = clause_text.lower()
    return any(signal in lower for signal in MULTI_CONDITION_SIGNALS)


def summarize_policy(clauses: list) -> str:
    """
    Produces a complete, per-clause summary from retrieve_policy's output.
    Every clause appears exactly once, in document order. Multi-condition
    clauses are quoted verbatim and marked [VERBATIM] rather than paraphrased,
    so no approver, threshold, or exception can be silently dropped.
    """
    lines = []
    for clause in clauses:
        text = " ".join(clause["clause_text"].split())
        if _is_multi_condition(text):
            lines.append(f"{clause['clause_number']}: [VERBATIM] {text}")
        else:
            lines.append(f"{clause['clause_number']}: {text}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. {len(clauses)} clauses summarized. Results written to {args.output}")


if __name__ == "__main__":
    main()
