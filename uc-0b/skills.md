skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and parses it into structured numbered sections for easier extraction.
    input: Path to the policy text file (string).
    output: Dictionary mapping clause numbers (e.g. '2.3') to their exact text content.
    error_handling: Refuses and exits if the file does not exist or is empty.

  - name: summarize_policy
    description: Takes the structured clause mapping and generates a summary that includes every critical clause, using verbatim quotes and highlighting binding verbs to prevent meaning drift.
    input: Dictionary of structured clauses (dict).
    output: Compiled summary string (string).
    error_handling: Raises an error if any of the 10 target clauses are missing from the input dictionary.
