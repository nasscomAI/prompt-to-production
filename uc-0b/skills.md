skills:
  - name: retrieve_policy
    description: Loads a policy text file and extracts structured numbered clauses.
    input: File path to a .txt policy document.
    output: Dictionary mapping clause numbers (e.g., 2.3, 2.4) to clause text.
    error_handling: Returns empty structure if file missing; raises readable error for invalid format.

  - name: summarize_policy
    description: Converts structured policy clauses into a summary while preserving all obligations and conditions.
    input: Dictionary of clause numbers mapped to clause text.
    output: String summary with each clause rewritten or quoted with its number.
    error_handling: If clause cannot be safely summarized, returns it verbatim and flags it.