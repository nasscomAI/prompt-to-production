skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and parses it into a list of structured clauses with section numbers and text.
    input: File path to the input text file (input_path).
    output: List of dictionaries, each containing 'clause_id' (e.g. '2.3') and 'text'.
    error_handling: Raises FileNotFoundError if the input file does not exist, and logs a warning for unnumbered text blocks.

  - name: summarize_policy
    description: Processes structured clauses into a summary, applying strict compliance, verbatim quoting, and flagging rules.
    input: List of dictionaries containing structured clauses.
    output: String representing the formatted summary.
    error_handling: Uses fallback descriptions or raises ValueError if required clauses are missing.
