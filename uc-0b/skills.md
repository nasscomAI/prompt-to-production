# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its document metadata plus structured numbered sections and clauses.
    input: path to a policy .txt file
    output: tuple (metadata, sections) where metadata is a list of header lines and sections is a list of (section_title, [(clause_id, clause_text)])
    error_handling: Raises FileNotFoundError with a clear message if the file is missing; skips decorative separator lines and blank lines; treats any non-numbered content under a section as continuation text of the current clause.

  - name: summarize_policy
    description: Produces a meaning-preserving digest where every clause appears once under its section, high-risk clauses are quoted verbatim and flagged [VERBATIM], and a completeness self-check is appended.
    input: (metadata, sections) returned by retrieve_policy
    output: summary string (one line per clause, section headers as structure, [VERBATIM] markers on trap clauses)
    error_handling: Verifies every source clause id appears in the output, checks clause 5.2 keeps both approvers, and scans for scope-bleed phrases; reports any violation instead of silently producing a lossy summary.
