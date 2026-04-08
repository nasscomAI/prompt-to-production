skills:
  - name: retrieve_policy
    description: >
      Reads a policy text file and extracts structured numbered clauses.
    input: >
      File path (string) to a .txt policy document.
    output: >
      A dictionary mapping clause numbers (e.g., "2.3") to their full text.
    error_handling: >
      If file is missing or unreadable, raises a clear error message and stops execution.
      Ignores non-numbered text safely.

  - name: summarize_policy
    description: >
      Converts structured policy clauses into a concise summary while preserving all obligations and conditions.
    input: >
      Dictionary of clause numbers mapped to clause text.
    output: >
      A formatted string summary where each clause is represented with its number and preserved meaning.
    error_handling: >
      If a clause is ambiguous or cannot be summarized without losing meaning,
      it is included verbatim and marked with [FLAGGED]. Ensures no clause is skipped.