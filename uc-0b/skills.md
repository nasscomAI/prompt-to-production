skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and extracts structured numbered sections and clauses.
    input: An absolute path to the text file (e.g. policy_hr_leave.txt).
    output: A dictionary mapping clause numbers (e.g., '2.3') to their exact text.
    error_handling: Raises FileNotFoundError if the path doesn't exist, or returns an empty dictionary if no clauses can be parsed.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary preserving all binding constraints.
    input: A dictionary of extracted clauses.
    output: A formatted string summary where each of the 10 critical clauses is listed with references and exact obligations.
    error_handling: If a critical clause is missing from the input, it raises a ValueError.
