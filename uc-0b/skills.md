# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: file_path (str) — path to the policy text file.
    output: A list of dicts, each with keys section_number, title, and clauses (list of clause strings).
    error_handling: >
      If the file does not exist or is empty, prints an error message and exits.
      If a section cannot be parsed, includes it as raw text with a parsing warning.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary preserving all clauses and conditions.
    input: List of structured sections from retrieve_policy.
    output: A text summary with one entry per clause, preserving clause numbers and all binding conditions.
    error_handling: >
      If a clause contains multiple conditions, all are preserved. If meaning
      loss is unavoidable, the clause is quoted verbatim and flagged with
      [VERBATIM].
