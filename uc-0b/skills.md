skills:
  - name: retrieve_policy
    description: Loads the raw HR Leave Policy text file and parses it into a dictionary of structured numbered sections and their corresponding text.
    input: Path to the raw policy text file as a string.
    output: A dictionary mapping clause numbers (e.g. '2.3', '5.2') to their raw clause text.
    error_handling: If the file path is invalid or empty, raises FileNotFoundError. If a line is malformed, logs it and skips it.

  - name: summarize_policy
    description: Takes the structured clause sections and produces a summarized policy document preserving all conditions, flagging complex clauses verbatim.
    input: Dictionary mapping clause numbers to their text.
    output: A single string representing the formatted policy summary.
    error_handling: If any of the required 10 critical clauses are missing from the input, raises a ValueError.
