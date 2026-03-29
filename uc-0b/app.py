import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CLAUSE_PATTERN = re.compile(r"^(?P<id>\d+\.\d+)\s+(?P<text>.+?)\s*$")
BANNED_SCOPE_BLEED_PHRASES = (
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
)
GROUND_TRUTH = {
    "2.3": ("must", "at least 14 calendar days in advance"),
    "2.4": ("must", "written approval"),
    "2.5": ("will", "regardless of subsequent approval"),
    "2.6": ("may", "maximum of 5"),
    "2.7": ("must", "January–March"),
    "3.2": ("requires", "within 48 hours"),
    "3.4": ("requires", "regardless of duration"),
    "5.2": ("requires", "Department Head and the HR Director"),
    "5.3": ("requires", "Municipal Commissioner"),
    "7.2": ("not permitted", "under any circumstances"),
}


class PolicyError(Exception):
    """Raised when the source policy cannot be processed safely."""


@dataclass(frozen=True)
class Clause:
    clause_id: str
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a clause-preserving summary for the UC-0B leave policy."
    )
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    return parser.parse_args()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def retrieve_policy(input_path: str) -> list[Clause]:
    """Load a .txt policy file and return structured numbered sections."""
    if not input_path:
        raise PolicyError("Invalid input: policy file path is required.")

    path = Path(input_path)
    if path.suffix.lower() != ".txt":
        raise PolicyError("Invalid input: policy file must be a .txt document.")
    if not path.exists():
        raise PolicyError(f"Invalid input: policy file not found: {path}")
    if not path.is_file():
        raise PolicyError(f"Invalid input: path is not a file: {path}")

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"Invalid input: unable to read policy file: {exc}") from exc

    clauses: list[Clause] = []
    current_id: str | None = None
    current_lines: list[str] = []

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        match = CLAUSE_PATTERN.match(stripped)
        if match:
            if current_id is not None:
                clauses.append(
                    Clause(current_id, normalize_text(" ".join(current_lines)))
                )
            current_id = match.group("id")
            current_lines = [match.group("text")]
            continue

        if current_id is not None and stripped and raw_line[:1].isspace():
            current_lines.append(stripped)

    if current_id is not None:
        clauses.append(Clause(current_id, normalize_text(" ".join(current_lines))))

    if not clauses:
        raise PolicyError(
            "Invalid input: document could not be reliably segmented into numbered clauses."
        )

    clause_ids = [clause.clause_id for clause in clauses]
    if len(clause_ids) != len(set(clause_ids)):
        raise PolicyError("Invalid input: duplicate clause identifiers detected.")

    for clause in clauses:
        if not clause.text:
            raise PolicyError(
                f"Invalid input: clause {clause.clause_id} is empty or ambiguous."
            )

    return clauses


def ensure_complete_and_ordered(clauses: Iterable[Clause]) -> list[Clause]:
    structured = list(clauses)
    if not structured:
        raise PolicyError("Invalid input: structured sections are missing.")

    previous: tuple[int, int] | None = None
    for clause in structured:
        if not isinstance(clause, Clause):
            raise PolicyError("Invalid input: structured sections are malformed.")
        match = re.fullmatch(r"(\d+)\.(\d+)", clause.clause_id)
        if not match:
            raise PolicyError(
                f"Invalid input: malformed clause identifier {clause.clause_id!r}."
            )
        current = (int(match.group(1)), int(match.group(2)))
        if previous is not None and current < previous:
            raise PolicyError("Invalid input: structured sections are out of order.")
        previous = current
        if not clause.text.strip():
            raise PolicyError(
                f"Invalid input: clause {clause.clause_id} is incomplete or empty."
            )

    missing_ground_truth = [cid for cid in GROUND_TRUTH if cid not in {c.clause_id for c in structured}]
    if missing_ground_truth:
        raise PolicyError(
            "Invalid input: required ground-truth clauses are missing: "
            + ", ".join(missing_ground_truth)
        )

    return structured


def validate_ground_truth(clauses: list[Clause]) -> None:
    by_id = {clause.clause_id: clause.text for clause in clauses}
    for clause_id, required_fragments in GROUND_TRUTH.items():
        text = by_id[clause_id].casefold()
        for fragment in required_fragments:
            if fragment.casefold() not in text:
                raise PolicyError(
                    f"Clause {clause_id} is ambiguous or incomplete; expected to preserve {fragment!r}."
                )

    clause_52 = by_id["5.2"].casefold()
    if "manager approval alone is not sufficient" not in clause_52:
        raise PolicyError(
            "Clause 5.2 is incomplete; it must preserve that manager approval alone is not sufficient."
        )


def clause_requires_verbatim_quote(clause: Clause) -> bool:
    text = clause.text.casefold()
    return any(
        token in text
        for token in (
            "must",
            "will",
            "requires",
            "not permitted",
            "forfeited",
            "approval",
        )
    )


def render_clause_summary(clause: Clause) -> str:
    rendered = normalize_text(clause.text)
    if clause_requires_verbatim_quote(clause):
        return f'[{clause.clause_id}] VERBATIM: "{rendered}"'
    return f"[{clause.clause_id}] {rendered}"


def summarize_policy(clauses: list[Clause]) -> str:
    """Produce a compliant summary with clause references."""
    structured = ensure_complete_and_ordered(clauses)
    validate_ground_truth(structured)

    summary_lines = [render_clause_summary(clause) for clause in structured]
    summary = "\n".join(summary_lines) + "\n"

    summary_ids = []
    for line in summary_lines:
        match = re.match(r"^\[(\d+\.\d+)\]", line)
        if not match:
            raise PolicyError("Output validation failed: clause reference missing.")
        summary_ids.append(match.group(1))

    source_ids = [clause.clause_id for clause in structured]
    if summary_ids != source_ids:
        raise PolicyError("Output validation failed: clause omission detected.")

    lowered_summary = summary.casefold()
    source_text = "\n".join(clause.text for clause in structured).casefold()
    for phrase in BANNED_SCOPE_BLEED_PHRASES:
        if phrase in lowered_summary and phrase not in source_text:
            raise PolicyError(f"Output validation failed: scope bleed detected: {phrase}")

    if "department head and the hr director" not in lowered_summary:
        raise PolicyError(
            "Output validation failed: clause 5.2 lost the dual-approver requirement."
        )

    return summary


def write_output(output_path: str, content: str) -> None:
    path = Path(output_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        write_output(args.output, summary)
    except PolicyError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
