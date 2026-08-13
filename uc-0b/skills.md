# skills.md — UC-0B
skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a plain-text policy file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: A list of sections, each with a section number, section heading, and its numbered clauses (e.g. {section: 2, heading: "ANNUAL LEAVE", clauses: ["2.1 ...", "2.2 ...", ...]}).
    error_handling: Raises a clear error if the file is missing or unreadable; if a section cannot be parsed into numbered clauses, returns the raw text block with a parse_warning flag instead of silently dropping it.

  - name: summarize_policy
    description: Produces a compliant clause-by-clause summary with clause references, preserving every condition and adding no external information.
    input: The structured sections from retrieve_policy, plus the clause inventory (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
    output: A summary where every inventory clause appears under its clause number with all conditions intact; format is plain text suitable for writing to summary_hr_leave.txt.
    error_handling: When a clause cannot be summarized without losing meaning, quotes it verbatim and marks it FLAGGED; when asked to cover material outside the source document, refuses and returns an explicit refusal message rather than guessing.
