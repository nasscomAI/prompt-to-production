"""
UC-0B — Summary That Changes Meaning
Loads policy documents, generates summaries, validates that meaning is preserved,
and highlights risky summaries that omit critical information.
"""

import argparse
import json
import re
from pathlib import Path


def load_policy(file_path: Path) -> str:
    """Load policy text from file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception:
        return ""


def extract_critical_elements(text: str) -> dict:
    """
    Extract numbers, deadlines, and key obligations from policy text.
    Returns dict with: numbers, deadlines, obligations, scope.
    """
    if not text:
        return {"numbers": [], "deadlines": [], "obligations": [], "scope": []}

    numbers = []
    # Match numeric values: 18 days, Rs 500, 30 days, etc.
    for m in re.finditer(r"(\d+)\s*(?:days?|weeks?|months?|hours?)", text, re.I):
        numbers.append(m.group(0))
    for m in re.finditer(r"Rs\s*[\d,]+", text, re.I):
        numbers.append(m.group(0))
    for m in re.finditer(r"[\d,]+\s*(?:lakh|crore|per cent)", text, re.I):
        numbers.append(m.group(0))

    deadlines = []
    for m in re.finditer(r"(?:within|within\s+)\s*(\d+)\s*(?:days?|hours?|working\s+days?)", text, re.I):
        deadlines.append(m.group(0))
    for m in re.finditer(r"at\s+least\s+(\d+)\s*(?:days?|hours?)", text, re.I):
        deadlines.append(m.group(0))

    obligations = []
    oblig_patterns = [
        r"must\s+[^.]*\.", r"requires?\s+[^.]*\.", r"mandatory\s+[^.]*\.",
        r"are\s+entitled\s+to\s+[^.]*\.", r"shall\s+[^.]*\.",
    ]
    for pat in oblig_patterns:
        for m in re.finditer(pat, text, re.I):
            obligations.append(m.group(0).strip()[:80])

    scope = []
    for m in re.finditer(r"(?:applies?\s+to|governs?\s+)([^.\n]+)", text, re.I):
        scope.append(m.group(1).strip()[:60])

    return {
        "numbers": list(dict.fromkeys(numbers)),
        "deadlines": list(dict.fromkeys(deadlines)),
        "obligations": obligations[:10],
        "scope": list(dict.fromkeys(scope))[:5],
    }


def generate_summary(text: str) -> str:
    """
    Build a 2–5 sentence summary from policy text using section extraction.
    Uses section headers and first sentences of key sections.
    """
    if not text or not text.strip():
        return "Unable to summarise: empty policy."

    lines = text.split("\n")
    sections = []
    current_section = []
    current_title = ""

    for line in lines:
        # Detect section headers (e.g., "1. PURPOSE", "2. ANNUAL LEAVE")
        m = re.match(r"^[\d.]+\s+([A-Z][A-Z\s&]+)$", line.strip())
        if m and len(line.strip()) < 60:
            if current_section:
                sections.append((current_title, " ".join(current_section)[:200]))
            current_title = m.group(1).strip()
            current_section = []
        elif line.strip() and not line.strip().startswith("═"):
            current_section.append(line.strip())

    if current_section:
        sections.append((current_title, " ".join(current_section)[:200]))

    # Build summary from first 3–4 meaningful sections
    summary_parts = []
    for title, content in sections[:5]:
        if title and content:
            first_sent = re.split(r"[.!?]", content)[0].strip()
            if first_sent and len(first_sent) > 20:
                summary_parts.append(f"{title}: {first_sent}.")

    summary = " ".join(summary_parts[:5])
    if len(summary) < 50:
        summary = " ".join(text.split()[:80]) + "..."

    return summary.strip()


def validate_summary(policy_text: str, summary: str, critical: dict) -> dict:
    """
    Check if summary preserves policy meaning. Flag risky summaries.
    Returns: valid, risky, omitted_critical
    """
    if not summary or not policy_text:
        return {"valid": False, "risky": True, "omitted_critical": ["Empty input"]}

    summary_lower = summary.lower()
    omitted = []

    for num in critical.get("numbers", [])[:8]:
        if num.lower() not in summary_lower and re.sub(r"\s+", "", num) not in re.sub(r"\s+", "", summary):
            omitted.append(num)

    for dl in critical.get("deadlines", [])[:5]:
        if dl.lower() not in summary_lower:
            omitted.append(dl)

    if critical.get("scope") and not any(s.lower() in summary_lower for s in critical["scope"][:2]):
        omitted.append("Scope/eligibility")

    risky = len(omitted) > 1
    valid = len(omitted) == 0

    return {
        "valid": valid,
        "risky": risky,
        "omitted_critical": omitted[:10],
    }


def process_policies(policy_dir: Path, output_path: Path | None) -> list:
    """Process all policy files in directory."""
    policy_files = list(policy_dir.glob("*.txt"))
    results = []

    for pf in sorted(policy_files):
        try:
            text = load_policy(pf)
            if not text.strip():
                results.append({
                    "policy_name": pf.name,
                    "summary": "",
                    "valid": False,
                    "risky": True,
                    "omitted_critical": ["Empty policy file"],
                })
                continue

            critical = extract_critical_elements(text)
            summary = generate_summary(text)
            validation = validate_summary(text, summary, critical)

            result = {
                "policy_name": pf.name,
                "summary": summary,
                "valid": validation["valid"],
                "risky": validation["risky"],
                "omitted_critical": validation["omitted_critical"],
            }
            results.append(result)
        except Exception as e:
            results.append({
                "policy_name": pf.name,
                "summary": "",
                "valid": False,
                "risky": True,
                "omitted_critical": [str(e)],
            })

    # Print results
    print("\n--- Policy Summary & Validation ---\n")
    for r in results:
        status = "RISKY" if r["risky"] else "OK"
        print(f"  [{status}] {r['policy_name']}")
        print(f"       Summary: {r['summary'][:120]}...")
        if r["omitted_critical"]:
            print(f"       Omitted: {r['omitted_critical']}")
        print()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"policies": results}, f, indent=2)
        print(f"  Results written to: {output_path}\n")

    # Write summary_hr_leave.txt (workshop requirement)
    uc0b_dir = Path(__file__).resolve().parent
    for r in results:
        if r["policy_name"] == "policy_hr_leave.txt":
            txt_path = uc0b_dir / "summary_hr_leave.txt"
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"POLICY: {r['policy_name']}\n")
                f.write(f"STATUS: {'RISKY' if r['risky'] else 'OK'}\n\n")
                f.write("SUMMARY:\n")
                f.write(r["summary"] + "\n\n")
                if r["omitted_critical"]:
                    f.write("OMITTED CRITICAL: " + ", ".join(r["omitted_critical"]) + "\n")
            print(f"  summary_hr_leave.txt written to: {txt_path}\n")
            break

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Validator")
    parser.add_argument("--input", default="data/policy-documents", help="Path to policy documents directory")
    parser.add_argument("--output", help="Path to write results JSON (optional)")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    policy_dir = Path(args.input)
    if not policy_dir.is_absolute():
        policy_dir = (Path.cwd() / args.input).resolve()
    if not policy_dir.exists() and (base / "data/policy-documents").exists():
        policy_dir = base / "data/policy-documents"
    output_path = Path(args.output) if args.output else None
    if output_path and not output_path.is_absolute():
        output_path = base / output_path

    process_policies(policy_dir, output_path)
    print("Done.")


if __name__ == "__main__":
    main()
