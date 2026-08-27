skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and structures it into numbered clauses.
    input:
      type: file_path
      format: string pointing to .txt file
    output:
      type: structured_data
      format: list of clauses with clause number and text
    error_handling:
      - If file path is invalid, return error message
      - If file is empty, return error indicating no content
      - If clauses cannot be identified, return parsing error

  - name: summarize_policy
    description: Generates a compliant summary from structured clauses while preserving all obligations and conditions.
    input:
      type: structured_data
      format: list of numbered clauses
    output:
      type: text
      format: summarized policy with clause references
    error_handling:
      - If any clause is missing, return error
      - If multi-condition clause loses a condition, return error
      - If additional information is introduced, reject output
      - If meaning is altered, quote original clause instead
