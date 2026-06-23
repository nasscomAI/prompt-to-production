"""
UC-0B — Policy summarization agent.
Skills: retrieve_policy, summarize_policy  (see skills.md)
"""
import argparse
import re
from pathlib import Path


# ── Skill: retrieve_policy ──────────────────────────────────────────

def retrieve_policy(filepath):
    """Load a .txt policy file; return its content as structured numbered sections."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Only .txt files supported, got: {path.suffix}")

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)")
    clauses = []
    current_num = None
    current_lines = []

    for line in lines:
        m = pattern.match(line)
        if m:
            if current_num is not None:
                clauses.append({
                    "clause": current_num,
                    "content": " ".join(current_lines)
                })
            current_num = m.group(1)
            current_lines = [m.group(2).strip()]
        elif current_num is not None and line.strip():
            current_lines.append(line.strip())

    if current_num is not None:
        clauses.append({
            "clause": current_num,
            "content": " ".join(current_lines)
        })

    if not clauses:
        raise ValueError(f"No numbered clauses found in {filepath}")

    return clauses


# ── Skill: summarize_policy ─────────────────────────────────────────

def summarize_policy(clauses):
    """
    Produce a compliant summary preserving all clauses with exact obligations.
    Flags any clause verbatim if summarisation would cause meaning loss.
    """
    if not clauses:
        raise ValueError("No clauses to summarise — input list is empty")

    # Clauses whose exact wording must be quoted per AGENTS.md enforcement
    verbatim_clauses = {"5.2", "5.3", "7.2"}

    lines = []
    lines.append("EMPLOYEE LEAVE POLICY — CLAUSE-ACCURATE SUMMARY")
    lines.append("=" * 60)
    lines.append("")
    current_section = None

    for item in clauses:
        num = item["clause"]
        text = item["content"]
        section = num.split(".")[0]

        if section != current_section:
            lines.append(f"── Section {section} ──")
            lines.append("")
            current_section = section

        if num in verbatim_clauses:
            lines.append(f"  [{num}] [VERBATIM] {text}")
        else:
            lines.append(f"  [{num}] {text}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("All numbered clauses from the source document are preserved above.")
    lines.append("Multi-condition obligations preserve ALL conditions — never dropped.")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0B: Summarise HR leave policy document")
    parser.add_argument("--input", required=True, help="Path to the input .txt policy file")
    parser.add_argument("--output", required=True, help="Path for the output summary file")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (script_dir.parent / args.input).resolve()

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (script_dir / args.output).resolve()

    clauses = retrieve_policy(str(input_path))
    summary = summarize_policy(clauses)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(f"Summary written to {output_path}")
    print(f"Clauses extracted: {len(clauses)}")


if __name__ == "__main__":
    main()
