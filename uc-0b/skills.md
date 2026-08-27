skills:
  - name: retrieve_policy
    description: Loads the policy text file and returns structured sections
    input: file path (string)
    output: structured text (string with numbered sections)
    error_handling: return error if file not found or empty

  - name: summarize_policy
    description: Summarizes policy while preserving all clauses and conditions
    input: structured policy text (string)
    output: summarized text with clause references
    error_handling: flag NEEDS_REVIEW if clauses missing or meaning changed