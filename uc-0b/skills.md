skills:
  - name: retrieve_policy
    description: Reads the raw text HR policy file and extracts sections and numbered clauses.
    input: string representing the path to the input text file
    output: list of dictionaries, where each dict has keys 'clause_id' and 'text'
    error_handling: Raises FileNotFoundError if the path is invalid, or ValueError if the file structure is empty or corrupt.

  - name: summarize_policy
    description: Generates a concise, non-softened summary for each clause, adhering strictly to multi-condition and binding verb constraints.
    input: list of dictionaries containing clause data
    output: string representing the formatted summary text grouped by section
    error_handling: Fall back to copying the original clause verbatim and logging a review flag if a clause cannot be summarized safely.
