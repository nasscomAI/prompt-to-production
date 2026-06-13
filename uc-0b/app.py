"""
UC-0B app.py — Summary That Changes Meaning
"""
import argparse
import re


def retrieve_policy(file_path: str) -> dict:
    """Load a .txt policy file, parse into structured numbered sections."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return {"error": "NO_CLAUSES_FOUND", "clauses": {}, "metadata": {}}

    clauses = {}
    metadata = {}

    header_match = re.search(
        r"^(.*?)EMPLOYEE LEAVE POLICY.*?Document Reference:\s*(\S+)\s*\n.*?Version:\s*(\S+)\s*\|.*?Effective:\s*(.+?)\n",
        content, re.DOTALL
    )
    if header_match:
        metadata["title"] = header_match.group(1).strip()
        metadata["doc_ref"] = header_match.group(2).strip()
        metadata["version"] = header_match.group(3).strip()
        metadata["effective"] = header_match.group(4).strip()

    current_clause = None
    current_text = []
    for line in content.split("\n"):
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if clause_match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
        elif current_clause and line.strip() and not line.strip().startswith("="):
            current_text.append(line.strip())
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()

    return {"clauses": clauses, "metadata": metadata}


def summarize_policy(parsed: dict) -> str:
    """Produce a compliant summary preserving all clauses, conditions, and binding verbs."""
    if "error" in parsed:
        return f"ERROR: {parsed['error']}\n"

    clauses = parsed["clauses"]
    metadata = parsed["metadata"]
    output_lines = []

    output_lines.append("=" * 60)
    output_lines.append("POLICY SUMMARY — Clause-Compliant")
    output_lines.append("=" * 60)
    if metadata:
        output_lines.append(f"Document: {metadata.get('title', 'N/A')}")
        output_lines.append(f"Reference: {metadata.get('doc_ref', 'N/A')}")
        output_lines.append(f"Version: {metadata.get('version', 'N/A')} | Effective: {metadata.get('effective', 'N/A')}")
    output_lines.append("")

    output_lines.append("CLAUSE INVENTORY")
    output_lines.append("-" * 60)
    output_lines.append(f"{'Clause':<10} {'Core Obligation':<40} {'Binding Verb':<15}")
    output_lines.append("-" * 60)

    binding_verbs = {
        "must": ["must", "must not", "must be"],
        "will": ["will", "will not", "will be"],
        "requires": ["requires", "required"],
        "may": ["may", "may not"],
        "not permitted": ["not permitted", "prohibited"],
    }

    for clause_num in sorted(clauses.keys(), key=lambda x: [int(p) for p in x.split(".")]):
        text = clauses[clause_num]
        core = text[:60] + "..." if len(text) > 60 else text
        verb = "—"
        text_lower = text.lower()
        for v, patterns in binding_verbs.items():
            if any(p in text_lower for p in patterns):
                verb = v
                break
        output_lines.append(f"{clause_num:<10} {core:<40} {verb:<15}")

    output_lines.append("")
    output_lines.append("CLAUSE-BY-CLAUSE SUMMARY")
    output_lines.append("-" * 60)

    multi_condition_keywords = {
        "5.2": ["department head", "hr director"],
        "3.2": ["48 hours", "3 or more", "consecutive"],
        "3.4": ["before or after", "regardless"],
        "2.4": ["written", "before", "verbal"],
        "5.3": ["30", "municipal commissioner"],
    }

    for clause_num in sorted(clauses.keys(), key=lambda x: [int(p) for p in x.split(".")]):
        text = clauses[clause_num]
        needs_verbatim = False

        if clause_num in multi_condition_keywords:
            keywords = multi_condition_keywords[clause_num]
            missing = [kw for kw in keywords if kw not in text.lower()]
            if missing:
                needs_verbatim = True

        if needs_verbatim:
            output_lines.append(f"\n{clause_num} [VERBATIM_REQUIRED]")
            output_lines.append(f"  {text}")
        else:
            output_lines.append(f"\n{clause_num}")
            output_lines.append(f"  {text}")

    output_lines.append("")
    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B — Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    parsed = retrieve_policy(args.input)
    summary = summarize_policy(parsed)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
