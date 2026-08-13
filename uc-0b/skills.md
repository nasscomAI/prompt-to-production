# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a plain text policy document.
    output: A list of dicts, each with keys {clause_number, clause_text, section}.
    error_handling: If file not found or empty, return error message and exit gracefully.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses and conditions.
    input: List of dicts from retrieve_policy.
    output: A plain text summary string with one entry per clause, preserving obligations and binding verbs.
    error_handling: If a clause is ambiguous or too complex to summarize, quote it verbatim and flag it.