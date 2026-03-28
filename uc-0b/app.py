"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> dict:
    """Load policy text and parse numbered clauses into structured sections."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            full_text = f.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Policy file not found: {input_path}") from exc
    except OSError as exc:
        raise OSError(f"Policy file is unreadable: {input_path}") from exc

    if not full_text.strip():
        raise ValueError("Policy file is empty.")

    sections = []
    current = None

    for raw_line in full_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        # Ignore visual separators and section headers that are not clause content.
        if re.match(r"^[═=\-]{5,}$", stripped):
            continue
        if re.match(r"^\d+\.\s+[A-Z]", stripped):
            continue

        match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        if match:
            if current:
                current["clause_text"] = " ".join(current["clause_text"].split())
                sections.append(current)
            current = {
                "clause_id": match.group(1),
                "clause_text": match.group(2).strip(),
            }
            continue

        if current:
            current["clause_text"] += f" {stripped}"

    if current:
        current["clause_text"] = " ".join(current["clause_text"].split())
        sections.append(current)

    if not sections:
        raise ValueError("No numbered clauses could be parsed from policy document.")

    return {"full_text": full_text, "sections": sections}


def summarize_policy(policy_struct: dict) -> str:
    """Generate clause-referenced, lossless summary for required clauses."""
    sections = policy_struct.get("sections", [])
    clause_map = {s["clause_id"]: s["clause_text"] for s in sections if "clause_id" in s and "clause_text" in s}

    summary_lines = [
        "UC-0B Compliant Summary (Clause Referenced)",
        "",
    ]

    for clause_id in REQUIRED_CLAUSES:
        text = clause_map.get(clause_id, "").strip()
        if not text:
            summary_lines.append(
                f"[{clause_id}] Clause missing from parsed source. [VERBATIM_REQUIRED]"
            )
            continue

        # Use source-faithful wording to avoid obligation softening and condition drop.
        summary_lines.append(f"[{clause_id}] {text}")

    return "\n".join(summary_lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    policy_struct = retrieve_policy(args.input)
    summary = summarize_policy(policy_struct)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
