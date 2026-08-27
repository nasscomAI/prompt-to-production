skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and extracts the structured numbered clauses.
    input: file_path (string) - Path to the policy text file.
    output: clauses (dictionary mapping clause numbers to raw clause text content).
    error_handling: If the file is missing, unreadable, or empty, raises FileNotFoundError or ValueError, prints an error to stderr, and exits non-zero.

  - name: summarize_policy
    description: Takes the extracted clauses and produces a compliant summary preserving all obligations, conditions, and references.
    input: clauses (dictionary mapping clause numbers to raw clause text content).
    output: summary (string) - Plain-text summary where every target clause is preserved with its obligations.
    error_handling: If any required clause is missing or cannot be parsed, or if a clause cannot be summarized without loss of meaning, quote it verbatim and flag it with [VERBATIM].
