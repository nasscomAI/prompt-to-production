skills:
  - name: retrieve_policy
    description: Loads HR policy text file and returns structured clauses.
    input: File path to .txt policy document.
    output: List of policy clauses (strings).
    error_handling: If file not found or empty, return error.

  - name: summarize_policy
    description: Generates summary preserving all clauses and conditions.
    input: List of policy clauses.
    output: Summary text with all clauses included.
    error_handling: If clause unclear, include it verbatim instead of modifying.