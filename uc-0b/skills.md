skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered sections.
    input: File path to the policy text file (string).
    output: A dictionary mapping section numbers/clause numbers to their text content.
    error_handling: Raises an error if the file cannot be read or is empty.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that explicitly preserves critical clauses.
    input: Dictionary of structured policy sections.
    output: A summary string where critical clauses are cited verbatim to prevent meaning loss.
    error_handling: Returns an empty summary or default warning message if no sections are provided.
