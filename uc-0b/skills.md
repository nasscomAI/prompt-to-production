skills:
  - name: retrieve_policy
    description: Loads the HR policy document and extracts numbered clauses.
    input: policy_hr_leave.txt file path
    output: structured list of clause numbers and clause text
    error_handling: raise error if document cannot be read or clauses cannot be extracted

  - name: summarize_policy
    description: Generates a compliant summary containing required policy clauses.
    input: structured clause list
    output: summary text containing the required clauses
    error_handling: if clauses are missing or ambiguous, preserve the original clause text