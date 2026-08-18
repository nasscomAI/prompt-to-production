skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause references and binding verbs preserved.
    input: File path to .txt policy document (string).
    output: Dict with numbered sections, each containing clause number, original text, binding verb, and core obligation.
    error_handling: Raises error if file not found; rejects file if numbered clauses are malformed; validates that all 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are present in source.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all clauses, conditions, and original meaning.
    input: Dict with numbered sections from retrieve_policy.
    output: Summarized policy text with all clause references, all conditions, binding verbs preserved exactly, and [VERBATIM] flags for clauses requiring quotation.
    error_handling: Rejects summaries missing any of the 10 clauses; detects and rejects condition drops in multi-condition obligations (e.g., clause 5.2 must preserve both Department Head AND HR Director, not just "requires approval"); detects scope bleed and rejects summaries with phrases like "standard practice", "typically", "generally expected"; validates all binding verbs match source exactly; requires [VERBATIM] flag if clause cannot be summarized without meaning loss.