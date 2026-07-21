skills:
  - name: retrieve_policy
    description: Reads a .txt policy file from disk and parses its content into structured numbered sections and clauses.
    input: file_path (string path to the .txt policy document).
    output: A structured dictionary mapping clause numbers (e.g. '2.3', '5.2') and section titles to their exact raw text content.
    error_handling: Raises FileNotFoundError if file is missing; returns an empty dictionary if file content is unreadable or malformed.

  - name: summarize_policy
    description: Takes structured policy sections/clauses and generates a compliant, lossless policy summary adhering strictly to all RICE enforcement rules.
    input: A structured dictionary of policy sections and clauses.
    output: A plain-text formatted summary string referencing every numbered clause and preserving all binding verbs and multi-condition obligations.
    error_handling: If any numbered clause is missing from the input, explicitly inserts a warning header and flags the missing clause in the summary.
