skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and converts it into structured numbered sections.
    input: string (file path to .txt policy document)
    output: list (structured sections with clause numbers and text)
    error_handling:
      - If file path is invalid, return an error message
      - If file is empty or unreadable, return an error
      - If clauses are not properly formatted, flag and stop processing

  - name: summarize_policy
    description: Generates a compliant summary of policy clauses while preserving all obligations and conditions.
    input: list (structured policy sections with clause numbers)
    output: string (summarized text with clause references)
    error_handling:
      - If any clause is missing, return an error
      - If conditions are dropped, reject summary
      - If extra information is added, reject summary
      - If summary cannot preserve meaning, quote clause and flag it