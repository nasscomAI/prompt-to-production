skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured sections and clauses.
    input: File path of the policy document (string).
    output: A dictionary mapping clause numbers (strings) to their raw text content (string).
    error_handling: Raises an explicit FileNotFoundError if the path is invalid or empty.

  - name: summarize_policy
    description: Compiles a summary of the policy document, ensuring all critical clauses are accounted for and no conditions are softened.
    input: A dictionary of structured clauses.
    output: A compiled markdown or plain text summary (string).
    error_handling: Raises a ValueError or logs a critical warning if any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing from the input dictionary.
