skills:
  - name: retrieve_policy
    description: Load the HR leave policy text and return it as a raw string.
    input: Path to a `.txt` policy file.
    output: Raw policy text string.
    error_handling: Raises a clear error if the file cannot be read or does not exist.

  - name: summarize_policy
    description: Convert structured numbered clauses into a clause-preserving summary.
    input: List of dictionaries containing clause IDs and normalized clause text.
    output: A single summary string that includes every numbered clause with clause references.
    error_handling: Raises an error if required clauses are missing or no numbered clauses are found.
