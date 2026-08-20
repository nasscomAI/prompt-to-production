# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections (header, section title, list of numbered clauses).
    input: file path (str) to a .txt policy document
    output: dict with keys header (list[str]) and sections (list of dicts with title and clauses list of (num, text) tuples)
    error_handling: Raises SystemExit with a clear message if the input file does not exist; tolerant of decorative separator lines and multi-line clauses.

  - name: summarize_policy
    description: Produces a clause-complete digest from structured sections, preserving every clause verbatim and verifying all required clauses are present.
    input: parsed policy dict from retrieve_policy
    output: str — the full summary text including a [VERBATIM] clause-by-clause body and a CLAUSE INVENTORY VERIFICATION footer
    error_handling: Always flags missing required clauses in the footer instead of silently omitting them.