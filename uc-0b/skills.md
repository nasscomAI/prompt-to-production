skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured sections and numbered clauses.
    input: String path to the policy text file.
    output: A structured list or dictionary mapping clause numbers to their exact text.
    error_handling: Raise an error if the file is missing or unreadable.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant, verbatim-heavy summary pointing directly to clause numbers.
    input: Structured policy data returned from retrieve_policy.
    output: A formatted string representing the complete, legally-compliant summary of the policy.
    error_handling: If a critical clause (e.g., 5.2) cannot be safely shortened, fallback to quoting it verbatim to ensure no condition dropping.
