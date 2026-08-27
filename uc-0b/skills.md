# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file, parses numbered sections, and returns structured content with clause numbers and obligations.
    input: File path to policy document (.txt file). Type: string path.
    output: Structured policy object with fields: clauses (list of objects with: clause_number, binding_verb, core_obligation, full_text). Type: list of dictionaries.
    error_handling: If file not found, raise FileNotFoundError with clear message. If file is empty or malformed (no numbered clauses detected), raise ValueError. Parse clause numbers as floats (e.g., 2.3, 5.2) to handle decimal notation.

  - name: summarize_policy
    description: Takes structured policy clauses and produces a compliant summary that preserves all clauses and multi-condition obligations without adding external context.
    input: Structured policy object from retrieve_policy (list of clause dictionaries). Type: list of dictionaries.
    output: Summary text with clause references in format "Clause X.X: [obligation]". Each clause appears exactly once. Multi-condition clauses list all conditions separated by AND. Type: string.
    error_handling: If any clause cannot be summarized without meaning loss, include full verbatim text from source and flag with [QUOTED]. If multi-condition obligation detected, validate that all conditions are preserved before returning. Never add contextual phrases; if tempted to add "as is standard practice" or similar, raise exception instead.
