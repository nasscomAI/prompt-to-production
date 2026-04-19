skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a structured list of numbered sections.
    input: Path to a .txt policy file.
    output: Structured representation of policy sections (e.g., list of strings or dicts with clause numbers).
    error_handling: Flags missing or inaccessible files; ensures that all numbered clauses are captured during extraction.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all obligations and references.
    input: Structured policy sections with clause numbers.
    output: A summary string where every clause is referenced and all conditions are intact.
    error_handling: If a multi-condition obligation is detected, it validates that all conditions are present; quotes verbatim if summarization causes meaning loss.
