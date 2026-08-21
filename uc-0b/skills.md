skills:
  - name: retrieve_policy
    description: Reads policy document and returns full text
    input: file path (string)
    output: full text or error message
    error_handling: returns EMPTY_DOCUMENT or FILE_NOT_FOUND

  - name: summarize_policy
    description: Converts policy text into clause-preserving summary
    input: raw text
    output: structured summary with all clauses
    error_handling: returns input error messages unchanged