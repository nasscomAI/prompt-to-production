"""
UC-0B — Summary That Changes Meaning
Deterministic, local, stdlib-only. Fix for clause omission: every required
clause from the policy specification must be explicitly represented in the
output. A required clause that is missing from the source document is reported
explicitly as having no applicable result instead of being silently dropped.
"""
import argparse
import re

REQUIRED_CLAUSES = (
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
)

NO_RESULT = "NO APPLICABLE RESULT — clause not found in source document."


def retrieve_policy(input_path: str) -> dict:
    """Load a .txt policy file and return {clause_number: clause_text}."""
    clauses = {}
    current_num = None
    buf = []

    def flush():
        if current_num is not None:
            clauses[current_num] = " ".join(buf).strip()

    with open(input_path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n").strip()
            if not line or all(ch in "\u2550 " for ch in line):
                flush()
                current_num = None
                buf = []
                continue
            if re.match(r"^\d+\.\s", line):
                flush()
                current_num = None
                buf = []
                continue
            m = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
            if m:
                flush()
                current_num = m.group(1)
                buf = [m.group(2)]
                continue
            if current_num is not None:
                buf.append(line)
    flush()
    return clauses


def summarize_policy(clauses: dict) -> list:
    """Return output lines for all required clauses, in specification order."""
    lines = []
    for num in REQUIRED_CLAUSES:
        text = clauses.get(num)
        if text:
            lines.append(f"[{num}] {text}")
        else:
            lines.append(f"[{num}] {NO_RESULT}")
    return lines


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as out:
        out.write("Employee Leave Policy — required-clause summary\n")
        out.write(
            "All 10 required clauses must appear below in specification order; "
            "none may be omitted.\n"
        )
        out.write("Required clauses: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2\n")
        out.write("=" * 60 + "\n")
        for line in summary:
            out.write(line + "\n")
        out.write("=" * 60 + "\n")
        out.write(
            f"Coverage: {len(summary)} of {len(REQUIRED_CLAUSES)} required clauses "
            "emitted; every clause number appears exactly once.\n"
        )
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
