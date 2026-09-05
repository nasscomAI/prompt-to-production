"""
UC-0B — HR Leave Policy Summarizer
Implements retrieve_policy and summarize_policy per agents.md + skills.md.
"""
import argparse
import os
import re
import time
from pathlib import Path

from google import genai
from google.genai import types

_MODEL = "gemini-3.5-flash-lite"
_CONFIG = types.GenerateContentConfig(
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)

GROUND_TRUTH_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

SCOPE_BLEED_PHRASES = (
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
)

CLAUSE_LINE_RE = re.compile(r"^(\d+\.\d+)\s+")
SECTION_HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z].+)$")
CLAUSE_START_RE = re.compile(r"^(\d+\.\d+)\s+(.+)$")
SUMMARY_CLAUSE_RE = re.compile(r"^\[?(\d+\.\d+)\]?\s*(.*)$")

GROUND_TRUTH_CHECKS = {
    "2.3": (r"14", r"advance|notice"),
    "2.4": (r"written", r"verbal.*not valid|verbal approval is not"),
    "2.5": (r"lop|loss of pay", r"regardless of subsequent"),
    "2.6": (r"\b5\b", r"forfeit|31\s*december|31\s*dec"),
    "2.7": (r"january|jan[\u2013\-]mar|first quarter", r"forfeit|must"),
    "3.2": (r"3|three", r"consecutive|48\s*hour|medical cert"),
    "3.4": (r"holiday|public holiday", r"regardless of duration|medical cert"),
    "5.2": (r"department head", r"hr director"),
    "5.3": (r"30", r"municipal commissioner"),
    "7.2": (r"not permitted|encashment during service", r"any circumstances|under any"),
}


def _load_env() -> None:
    if os.environ.get("GEMINI_API_KEY"):
        return

    candidates = [
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for env_path in candidates:
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value
        if os.environ.get("GEMINI_API_KEY"):
            return


def _get_client() -> genai.Client:
    _load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Export it or add it to .env in the project root."
        )
    return genai.Client(api_key=api_key)


_client = None


def _client_instance() -> genai.Client:
    global _client
    if _client is None:
        _client = _get_client()
    return _client


def retrieve_policy(path: str) -> dict:
    resolved = os.path.abspath(path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Input file not found: {resolved}")

    content = Path(resolved).read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"File contains no policy content: {resolved}")

    lines = content.splitlines()
    document_title = next(
        (line.strip() for line in lines if line.strip() and not line.startswith("═")),
        "Unknown Policy",
    )

    sections = []
    current_heading = ""
    current_id = None
    current_text: list[str] = []

    def flush_clause() -> None:
        nonlocal current_id, current_text
        if current_id:
            sections.append({
                "clause_id": current_id,
                "heading": current_heading,
                "text": " ".join(current_text).strip(),
            })
        current_id = None
        current_text = []

    for line in lines:
        if line.startswith("═"):
            continue

        section_match = SECTION_HEADING_RE.match(line.strip())
        if section_match and "." not in section_match.group(1):
            flush_clause()
            current_heading = section_match.group(2).strip()
            continue

        clause_match = CLAUSE_START_RE.match(line.strip())
        if clause_match:
            flush_clause()
            current_id = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
            continue

        if current_id and line.startswith("    "):
            current_text.append(line.strip())

    flush_clause()

    if not sections:
        raise ValueError(f"Could not parse numbered sections from: {resolved}")

    found_ids = {s["clause_id"] for s in sections}
    missing_ground_truth = GROUND_TRUTH_CLAUSES - found_ids
    if missing_ground_truth:
        raise ValueError(
            f"Missing ground-truth clause IDs in parsed output: "
            f"{', '.join(sorted(missing_ground_truth))}"
        )

    return {"document_title": document_title, "sections": sections}


def _sections_by_id(sections: list[dict]) -> dict[str, dict]:
    return {s["clause_id"]: s for s in sections}


def _build_summarize_prompt(policy: dict, correction: str | None = None) -> str:
    clause_block = "\n".join(
        f"{s['clause_id']}: {s['text']}" for s in policy["sections"]
    )
    base = f"""You are an HR leave policy summarization engine for municipal government use.

Summarize the policy below. Follow these rules exactly:
1. Include EVERY numbered clause from the source — one summary line per clause.
2. Format each line as: [clause_id] summary text
3. Preserve ALL conditions in multi-condition obligations — never drop one silently.
4. Clause 5.2 MUST name both Department Head AND HR Director as required approvers.
5. Do NOT soften binding verbs (must, will, requires, not permitted, may, forfeited).
6. Do NOT add information not in the source — no phrases like "as is standard practice",
   "typically in government organisations", or "employees are generally expected to".
7. If a clause cannot be summarised without meaning loss, quote it verbatim and append [VERBATIM].

Document: {policy['document_title']}

SOURCE CLAUSES:
{clause_block}

Output ONLY the summary lines, one per clause, in clause_id order. No preamble."""
    if correction:
        return f"{base}\n\nCORRECTION REQUIRED:\n{correction}"
    return base


def _call_llm(prompt: str) -> str:
    last_error = None
    for attempt in range(3):
        try:
            response = _client_instance().models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=_CONFIG,
            )
            time.sleep(1)
            return response.text.strip()
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Summarization failed: {last_error}") from last_error


def _parse_summary_lines(summary: str) -> dict[str, str]:
    lines: dict[str, str] = {}
    for raw_line in summary.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = SUMMARY_CLAUSE_RE.match(line)
        if match:
            lines[match.group(1)] = match.group(2).strip()
    return lines


def _clause_line_text(summary: str, clause_id: str) -> str:
    for raw_line in summary.splitlines():
        match = SUMMARY_CLAUSE_RE.match(raw_line.strip())
        if match and match.group(1) == clause_id:
            return match.group(2)
    return ""


def _check_patterns(text: str, patterns: tuple[str, ...]) -> bool:
    lower = text.lower()
    return all(re.search(pat, lower) for pat in patterns)


def _validate_summary(summary: str, expected_clause_ids: set[str]) -> list[str]:
    errors: list[str] = []
    found_ids = set(_parse_summary_lines(summary).keys())

    missing = expected_clause_ids - found_ids
    if missing:
        errors.append(
            f"Missing clauses: {', '.join(sorted(missing))}"
        )

    lower_summary = summary.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in lower_summary:
            errors.append(f"Scope bleed phrase detected: {phrase}")

    for clause_id, patterns in GROUND_TRUTH_CHECKS.items():
        line_text = _clause_line_text(summary, clause_id)
        if not line_text:
            continue
        if not _check_patterns(line_text, patterns):
            errors.append(
                f"Clause {clause_id} does not preserve required obligations/conditions"
            )

    return errors


def _format_verbatim_line(section: dict) -> str:
    return f"[{section['clause_id']}] {section['text']} [VERBATIM]"


def _replace_clause_line(summary: str, clause_id: str, new_line: str) -> str:
    output_lines = []
    replaced = False
    for raw_line in summary.splitlines():
        match = SUMMARY_CLAUSE_RE.match(raw_line.strip())
        if match and match.group(1) == clause_id:
            output_lines.append(new_line)
            replaced = True
        else:
            output_lines.append(raw_line)
    if not replaced:
        output_lines.append(new_line)
    return "\n".join(output_lines).strip() + "\n"


def summarize_policy(policy: dict, output_path: str) -> str:
    sections = policy.get("sections")
    if not sections:
        raise ValueError("No policy sections were provided")

    sections_map = _sections_by_id(sections)
    expected_ids = set(sections_map.keys())

    missing_ground_truth = GROUND_TRUTH_CLAUSES - expected_ids
    if missing_ground_truth:
        raise ValueError(
            f"Missing ground-truth clauses in input sections: "
            f"{', '.join(sorted(missing_ground_truth))}"
        )

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if not os.path.isdir(out_dir) or not os.access(out_dir, os.W_OK):
        raise IOError(f"Output directory does not exist or is not writable: {out_dir}")

    summary = _call_llm(_build_summarize_prompt(policy))
    errors = _validate_summary(summary, expected_ids)

    if errors:
        correction = "\n".join(f"- {e}" for e in errors)
        summary = _call_llm(_build_summarize_prompt(policy, correction=correction))
        errors = _validate_summary(summary, expected_ids)

    if errors:
        five_two_errors = [e for e in errors if "5.2" in e]
        other_errors = [e for e in errors if "5.2" not in e]

        if five_two_errors and "5.2" in sections_map:
            verbatim = _format_verbatim_line(sections_map["5.2"])
            summary = _replace_clause_line(summary, "5.2", verbatim)
            errors = _validate_summary(summary, expected_ids)
            other_errors = [e for e in errors if "5.2" not in e]

        if other_errors:
            raise ValueError(
                "Summary validation failed after retry:\n"
                + "\n".join(f"- {e}" for e in other_errors)
            )

    if not summary.endswith("\n"):
        summary += "\n"

    Path(output_path).write_text(summary, encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summarize_policy(policy, args.output)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
