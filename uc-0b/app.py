"""
UC-0B app.py — Policy Summarizer

Implements the retrieve_policy / summarize_policy workflow described in
README.md, agents.md, and skills.md:

  retrieve_policy(path)     -> parses a .txt HR policy file into structured,
                                numbered sections/clauses.
  summarize_policy(document) -> produces a clause-referenced summary that
                                preserves every clause and every condition,
                                quoting binding/multi-condition clauses
                                verbatim instead of paraphrasing them.

See README.md for the run command and the ground-truth clause table this
implementation is checked against.
"""
import argparse
import re
import sys


class PolicyRetrievalError(Exception):
    """Raised when the input policy file cannot be loaded or parsed."""


class PolicySummaryError(Exception):
    """Raised when a structured document cannot be safely summarized."""


# "1. PURPOSE AND SCOPE" — an all-caps section title.
SECTION_RE = re.compile(r'^(\d+)\.\s+([A-Z][A-Z0-9 \-/&,()]*)$')
# "2.3 Employees must submit..." — a numbered clause.
CLAUSE_RE = re.compile(r'^(\d+\.\d+)\s+(.*)$')
# "═══...═══" divider lines used in the source document.
BAR_RE = re.compile(r'^═+$')

# Keywords that mark an obligation as binding and/or carrying more than one
# condition (a named approver, a numeric threshold, a deadline, an
# exception). Clauses matching these are quoted verbatim rather than
# paraphrased, per agents.md enforcement rule 4.
BINDING_KEYWORDS = re.compile(
    r'\b(must|will|shall|requires?|required|not permitted|regardless|'
    r'only|before|prior to|maximum|minimum|within|not sufficient|'
    r'not valid|not considered|cannot)\b',
    re.IGNORECASE,
)


def retrieve_policy(path):
    """
    Load a .txt policy file and parse it into structured numbered sections.

    Returns a dict:
      {
        "metadata": [str, ...],           # header lines before section 1
        "sections": [
          {
            "number": "2",
            "title": "ANNUAL LEAVE",
            "clauses": [{"number": "2.1", "text": "..."}, ...],
          },
          ...
        ],
      }
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise PolicyRetrievalError(f"Input policy file not found: {path}")
    except IsADirectoryError:
        raise PolicyRetrievalError(f"Input path is a directory, not a file: {path}")
    except PermissionError:
        raise PolicyRetrievalError(f"Permission denied reading input file: {path}")
    except UnicodeDecodeError as e:
        raise PolicyRetrievalError(f"Could not decode {path} as UTF-8 text: {e}")

    metadata = []
    sections = []
    current_section = None
    current_clause = None
    seen_first_section = False

    for line in raw.splitlines():
        stripped = line.strip()

        if not stripped or BAR_RE.match(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        clause_match = CLAUSE_RE.match(stripped)

        if section_match:
            current_clause = None
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            seen_first_section = True
            continue

        if clause_match and current_section is not None:
            current_clause = {
                "number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            continue

        if not seen_first_section:
            metadata.append(stripped)
            continue

        if current_clause is not None:
            # Continuation of a wrapped clause line (indented, no leading
            # clause number of its own) — fold it back into the clause text
            # exactly as written, just without the source line-wrap.
            current_clause["text"] = (current_clause["text"] + " " + stripped).strip()
        # Any other stray line (e.g. text directly under a section header
        # before its first numbered clause) is not attributable to a
        # specific clause, so it is intentionally not merged anywhere
        # rather than guessed at.

    if not sections or not any(s["clauses"] for s in sections):
        raise PolicyRetrievalError(
            f"No numbered clauses (e.g. '2.3 ...') found in {path}; "
            "nothing to summarize."
        )

    return {"metadata": metadata, "sections": sections}


def _is_binding_or_multicondition(text):
    return BINDING_KEYWORDS.search(text) is not None


def summarize_policy(document):
    """
    Produce a clause-referenced summary from the structured document
    returned by retrieve_policy.

    Every clause number in the source is preserved and tagged under its
    original section. Clauses that read as binding and/or multi-condition
    obligations are kept verbatim and flagged "(VERBATIM)" rather than
    paraphrased, so no condition or obligation strength can be silently
    dropped or softened.
    """
    sections = document.get("sections") if document else None
    if not sections or not any(s.get("clauses") for s in sections):
        raise PolicySummaryError(
            "No structured sections/clauses supplied to summarize_policy; "
            "refusing to produce a summary."
        )

    lines = []
    metadata = document.get("metadata") or []
    if metadata:
        lines.extend(metadata)
        lines.append("")

    lines.append("POLICY SUMMARY (clause-referenced extract)")
    lines.append(
        "Every numbered clause from the source document is listed below "
        "under its original section, in source order. Clauses carrying a "
        "binding obligation and/or more than one condition (approver, "
        "threshold, deadline, exception) are quoted verbatim and flagged "
        "(VERBATIM) to avoid meaning loss."
    )
    lines.append("")

    for section in sections:
        if not section["clauses"]:
            continue
        lines.append(f'{section["number"]}. {section["title"]}')
        for clause in section["clauses"]:
            tag = f'[{clause["number"]}]'
            if _is_binding_or_multicondition(clause["text"]):
                lines.append(f'  {tag} (VERBATIM) {clause["text"]}')
            else:
                lines.append(f'  {tag} {clause["text"]}')
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: summarize an HR leave policy document while "
        "preserving every numbered clause and every condition."
    )
    parser.add_argument("--input", required=True, help="Path to the source .txt policy file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    try:
        document = retrieve_policy(args.input)
        summary = summarize_policy(document)
    except (PolicyRetrievalError, PolicySummaryError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
    except IsADirectoryError:
        print(f"Error: output path is a directory, not a file: {args.output}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: permission denied writing output file: {args.output}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: could not write output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
