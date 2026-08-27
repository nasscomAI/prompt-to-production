skills:
  - name: retrieve_policy
    description: Reads a .txt file containing the policy document and returns the text parsed into structured numbered sections.
    input: file_path (str)
    output: A list of dicts, each with 'clause_id' (str) and 'text' (str)
    error_handling: Raise file not found if the path is invalid.

  - name: summarize_policy
    description: Takes structured clauses and produces a strict, compliant summary referencing every single clause. preserves multi-condition obligations.
    input: list of clauses (dicts)
    output: A formatted string representing the final summary
    error_handling: If a clause is missing or cannot be parsed, output a warning.
