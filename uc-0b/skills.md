skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and extracts structured numbered clauses.
    input: File path to .txt policy document
    output: List of strings where each item represents a numbered clause (e.g., "2.3 ...")
    error_handling: If file is missing or unreadable, return error message and stop execution

  - name: summarize_policy
    description: Generates a compliant summary ensuring all clauses and conditions are preserved without meaning loss.
    input: List of structured policy clauses
    output: List of summarized clauses with original clause numbers preserved
    error_handling: If any clause is missing or conditions are incomplete, reject summary and flag error for correction