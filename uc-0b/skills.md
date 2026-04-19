# skills.md — UC-0B

skills:
  - name: retrieve_policy
    description: Loads a UTF-8 policy .txt file from disk and returns the full text for parsing.
    input: "Filesystem path to a single policy file (string or Path)."
    output: "Raw policy text (string)."
    error_handling: "If the file is missing or not readable, raise a clear error; do not substitute placeholder policy text."

  - name: summarize_policy
    description: Parses numbered clauses, ensures the ten mandatory clauses are present, and writes a compliant summary with verbatim preserved clauses.
    input: "Structured map of clause id (e.g. '5.2') to clause text, plus optional metadata (document id, version)."
    output: "Final summary text suitable for summary_hr_leave.txt."
    error_handling: "If any mandatory clause id is missing from the source map, fail fast with an explicit list of missing clauses."
