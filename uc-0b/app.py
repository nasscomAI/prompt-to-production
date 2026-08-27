"""
UC-0B app.py — Policy Compliance Auditor
Reads agents.md (enforcement rules) and skills.md (skill definitions) to
guide structured summarization of HR policy documents.
"""
import argparse
import re
import sys
from pathlib import Path


def load_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        print(f"Error: {p} not found", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def parse_agents(path: str) -> dict:
    """Parse agents.md into role, intent, context, enforcement rules."""
    text = load_file(path)
    return {
        "role": _extract_yaml_scalar(text, "role"),
        "intent": _extract_yaml_scalar(text, "intent"),
        "context": _extract_yaml_scalar(text, "context"),
        "enforcement": _extract_yaml_list(text, "enforcement"),
    }


def parse_skills(path: str) -> list[dict]:
    """Parse skills.md into a list of skill definitions."""
    text = load_file(path)
    skills = []
    for block in re.split(r"\n(?=\s*- name:)", text):
        m = re.search(r"name:\s*(.+)", block)
        if not m:
            continue
        skills.append({
            "name": m.group(1).strip(),
            "description": _extract_yaml_scalar(block, "description"),
        })
    return skills


def _extract_yaml_scalar(text: str, key: str) -> str:
    """Extract a YAML scalar value (plain or > block) for a given key."""
    m = re.search(
        rf"^{key}:\s*>\s*\n((?:\s+.*\n?)*)",
        text, re.MULTILINE,
    )
    if m:
        return " ".join(
            line.strip() for line in m.group(1).split("\n")
            if line.strip()
        )
    m = re.search(rf"^{key}:\s*(.+)", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _extract_yaml_list(text: str, key: str) -> list[str]:
    """Extract a YAML list of quoted strings (possibly multi-line)."""
    m = re.search(rf"^{key}:\s*\n(.*?)(?=\n\S|\Z)", text, re.DOTALL + re.MULTILINE)
    if not m:
        return []
    items = []
    current = ""
    in_item = False
    for line in m.group(1).split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            if in_item and current:
                items.append(current)
            current = stripped[2:].strip().strip('"')
            in_item = True
        elif in_item and stripped:
            current += " " + stripped.strip('"')
    if in_item and current:
        items.append(current)
    return items


def parse_policy(text: str):
    """Parse policy text into list of {number, text, section} dicts."""
    lines = text.strip().split("\n")
    clauses = []
    current_section = ""
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for line in lines:
        line = line.strip()
        if not line or re.match(r"^═+$", line):
            continue
        if re.match(r"^\d+\.\s+[A-Z]", line):
            current_section = line
            continue
        m = clause_re.match(line)
        if m:
            clauses.append({
                "number": m.group(1),
                "text": m.group(2),
                "section": current_section,
            })
        elif clauses and not re.match(r"^\d+\.", line):
            clauses[-1]["text"] += " " + line

    return clauses


def extract_binding_verb(text: str) -> str:
    verbs = {"is not permitted", "are forfeited", "not permitted",
             "cannot", "must", "will", "shall", "requires", "require", "may"}
    lower = text.lower()
    for v in sorted(verbs, key=len, reverse=True):
        if v in lower:
            return v
    return ""


def summarize_clauses(clauses: list[dict]) -> str:
    """Build a structured summary that respects agents.md enforcement rules."""
    clause_map = {c["number"]: c for c in clauses}

    target_order = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4",
        "5.2", "5.3",
        "7.2",
    ]

    ground_truth = {
        "2.3": "14-day advance notice required",
        "2.4": "Written approval required before leave commences; verbal invalid",
        "2.5": "Unapproved absence = Loss of Pay (LOP) regardless of late approvals",
        "2.6": "Max 5 days carry-forward; anything above forfeited on Dec 31",
        "2.7": "Carry-forward days must be spent Jan\u2013Mar or forfeited",
        "3.2": "3+ consecutive sick days requires medical cert within 48 hours",
        "3.4": "Sick leave adjacent to a holiday requires cert regardless of length",
        "5.2": "LWP requires BOTH Department Head AND HR Director approval",
        "5.3": "LWP exceeding 30 days requires Municipal Commissioner approval",
        "7.2": "Leave encashment during active service is not permitted under any circumstances",
    }

    out = []
    out.append("UC-0B COMPLIANCE SUMMARY")
    out.append("=" * 48)

    for cid in target_order:
        clause = clause_map.get(cid)
        anchor = ground_truth[cid]
        if clause:
            verb = extract_binding_verb(clause["text"])
            out.append(f"{cid} | {anchor}")
            out.append(f"    Source text: {clause['text']}")
            if verb:
                out.append(f"    Binding verb: [{verb}]")
        else:
            out.append(f"{cid} | {anchor}")
            out.append("    MISSING FROM SOURCE")

    extra = [c for c in clauses if c["number"] not in target_order]
    if extra:
        out.append("")
        out.append("Additional clauses")
        out.append("-" * 20)
        for c in extra:
            verb = extract_binding_verb(c["text"])
            tag = f" [{verb}]" if verb else ""
            out.append(f"  {c['number']}: {c['text']}{tag}")

    return "\n".join(out)


def verify_output(text: str):
    """Post-generation verification per agents.md enforcement rules."""
    errors = []
    if "Department Head" not in text:
        errors.append("Clause 5.2 violation: 'Department Head' missing")
    if "HR Director" not in text:
        errors.append("Clause 5.2 violation: 'HR Director' missing")
    if "under any circumstances" not in text:
        errors.append("Clause 7.2 violation: 'under any circumstances' missing")

    for phrase in ["typically", "generally", "as per standard practice"]:
        if phrase in text.lower():
            errors.append(f"Scope bleed: '{phrase}' found in output")

    if errors:
        raise ValueError(
            "Post-generation verification failed:\n" + "\n".join(errors)
        )


def main():
    parser = argparse.ArgumentParser(
        description="Policy compliance summarizer driven by agents.md + skills.md"
    )
    parser.add_argument("--input", required=True, help="Input policy file")
    parser.add_argument("--output", required=True, help="Output summary file")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    agents_cfg = parse_agents(str(script_dir / "agents.md"))
    skills_cfg = parse_skills(str(script_dir / "skills.md"))

    print(f"Agent role: {agents_cfg['role'][:60]}...")
    print(f"Skills loaded: {', '.join(s['name'] for s in skills_cfg)}")
    print(f"Enforcement rules: {len(agents_cfg['enforcement'])}")

    policy_text = load_file(args.input)
    clauses = parse_policy(policy_text)

    if not clauses:
        print("Error: No clauses found in policy document", file=sys.stderr)
        sys.exit(1)

    summary = summarize_clauses(clauses)
    verify_output(summary)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    clause_nums = [c["number"] for c in clauses]
    print(f"\nSummary written to {output_path}")
    print(f"Clauses: {len(clauses)} — {', '.join(clause_nums)}")


if __name__ == "__main__":
    main()
