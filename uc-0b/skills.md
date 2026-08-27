skills:
  - name: retrieve_policy
    description: Reads the input text policy document and parses it into structured sections and numbered clauses.
    input: Path to the input policy document file (.txt).
    output: A dictionary mapping clause numbers (e.g., '2.3') to their full text content.
    error_handling: Raises an FileNotFoundError if the input file does not exist, or returns an empty dictionary if no clauses are found.

  - name: summarize_policy
    description: Summarizes the parsed clauses, ensuring all 10 target clauses are represented with exact obligations and conditions preserved.
    input: A dictionary of parsed clauses.
    output: A string containing the structured summary with clear clause numbers.
    error_handling: Logs warning messages if any of the target clauses are missing from the input data.
