skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as an ordered list of numbered sections with their clauses.
    input: File path (string) — absolute or relative path to the .txt policy document.
    output: >
      A dict with keys being section numbers (e.g., "1", "2") mapped to a
      list of clause dicts: {clause_id: str, text: str}. Returns None on
      file-not-found or read error.
    error_handling: >
      If the file path is invalid or the file cannot be opened, raise a
      FileNotFoundError with a descriptive message and halt execution.
      If the file is empty or contains no recognisable clause structure,
      raise a ValueError explaining the problem — do not produce partial output.


  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant plain-text summary preserving all clauses, binding verbs, and multi-condition obligations.
    input: >
      Structured dict from retrieve_policy — {section_id: [{clause_id, text}]}.
      Also accepts the section heading labels (dict mapping section_id to heading string).
    output: >
      A formatted plain-text string containing every clause summarised
      with its clause reference number, binding verbs intact, all conditions
      preserved. Multi-condition clauses are flagged inline. Output is
      suitable for writing directly to a .txt file.
    error_handling: >
      If any clause in the critical enforcement list (2.3, 2.4, 2.5, 2.6,
      2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is missing from the input, raise a
      ValueError identifying the missing clause — do not produce output
      with missing critical clauses. If a clause text is too complex to
      summarise without loss, emit it verbatim prefixed with [VERBATIM].
