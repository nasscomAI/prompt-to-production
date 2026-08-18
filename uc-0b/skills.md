# skills.md

skills:
  - name: retrieve_policy
    description: Loads the HR policy text from a .txt file and returns the numbered content in a structured form for clause-by-clause review.
    input: A file path to the policy document as a string.
    output: The raw policy text, grouped by numbered sections and clauses for later summarisation.
    error_handling: If the file is empty or missing, raises a clear validation error rather than silently summarising nothing.

  - name: summarize_policy
    description: Reads the structured policy sections and produces a compliant summary that keeps every required clause and all legal conditions intact.
    input: The loaded policy text as a string.
    output: A plain-text summary file containing each required clause in the exact required wording and numbered references.
    error_handling: If any required clause is missing or a condition would be dropped, the function fails loudly and refuses to paraphrase the clause away.
