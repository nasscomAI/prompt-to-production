skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts its structured numbered clauses.
    input: Path to the input policy text file.
    output: Dictionary mapping clause numbers (strings) to their corresponding text.
    error_handling: Raises FileNotFoundError if input file doesn't exist, logs parsing issues.

  - name: summarize_policy
    description: Formats a structured summary of the 10 target clauses, ensuring no softening or condition drops.
    input: Dictionary of extracted policy clauses.
    output: A formatted string representing the summary of the clauses.
    error_handling: Asserts that all 10 target clauses are present, otherwise falls back to a warning/error message.
