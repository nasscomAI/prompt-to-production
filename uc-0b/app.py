"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_RE = re.compile(r"^\d+\.\s+")


def retrieve_policy(file_path: str) -> list[dict[str, str]]:
    clauses: list[dict[str, str]] = []
    current_id = None
    current_lines: list[str] = []

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            match = CLAUSE_RE.match(line.strip())

            if match:
                if current_id is not None:
                    clauses.append(
                        {
                            "clause_id": current_id,
                            "text": " ".join(current_lines).strip(),
                        }
                    )
                current_id = match.group(1)
                current_lines = [match.group(2).strip()]
                continue

            if current_id is not None:
                cont = line.strip()
                if not cont:
                    continue
                if cont.startswith("═"):
                    continue
                if SECTION_HEADER_RE.match(cont):
                    continue
                if cont.isupper() and " " in cont:
                    continue
                if cont:
                    current_lines.append(cont)

    if current_id is not None:
        clauses.append(
            {
                "clause_id": current_id,
                "text": " ".join(current_lines).strip(),
            }
        )

    if not clauses:
        raise ValueError("No numbered clauses found in input policy file.")

    return clauses


def _is_high_risk(clause_text: str) -> bool:
    text = clause_text.lower()
    risk_markers = [
        " and ",
        " or ",
        "regardless",
        "not valid",
        "not permitted",
        "forfeited",
        "requires",
        "must",
    ]
    return any(marker in text for marker in risk_markers)


def summarize_policy(clauses: list[dict[str, str]]) -> str:
    lines = ["Compliant HR Leave Policy Summary (Clause-Preserved)", ""]

    for clause in clauses:
        cid = clause["clause_id"]
        ctext = clause["text"]

        if _is_high_risk(ctext):
            lines.append(f"{cid}: \"{ctext}\" [quoted-verbatim]")
        else:
            lines.append(f"{cid}: {ctext}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Summary That Changes Meaning - compliant summarizer"
    )
    parser.add_argument("--input", required=True, help="Path to source policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Wrote compliant summary with {len(clauses)} clauses to {args.output}")

if __name__ == "__main__":
    main()
