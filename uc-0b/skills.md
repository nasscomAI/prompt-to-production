# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document (string).
    output: Structured dict mapping clause numbers (e.g. "2.3", "5.2") to their full text content.
    error_handling: Returns an error if the file does not exist, is empty, or contains no recognisable numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Dict of clause_number → clause_text (from retrieve_policy).
    output: Summary string where every clause is present with its number, conditions intact, and any unsummarisable clauses quoted verbatim with a flag.
    error_handling: Refuses to produce output if any clause cannot be faithfully represented; returns which clauses failed and why.
