skills:
  - name: retrieve_policy
    description: Loads a text policy file and parses it into structured numbered clauses.
    input: String path to the policy text file.
    output: A dictionary mapping clause numbers (e.g., '2.3') to their corresponding text.
    error_handling: Raises FileNotFoundError if the file cannot be accessed, or returns an empty dictionary if the format is invalid.

  - name: summarize_policy
    description: Takes the structured clauses dictionary and extracts the 10 target clauses, wrapping them in a verbatim format to prevent any condition drops or softening.
    input: A dictionary of structured clauses.
    output: A string containing the formatted summary text.
    error_handling: For any missing target clauses, appends a warning tag indicating that the clause is missing from the source.
