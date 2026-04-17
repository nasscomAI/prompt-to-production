skills:
  - name: retrieve_policy
    description: Load and parse the HR policy document into structured numbered clauses
    input: file path to .txt policy document
    output: structured list of clauses with clause numbers and text
    error_handling: Return error if file is missing, unreadable, or does not contain structured clauses

  - name: summarize_policy
    description: Generate a summary preserving all clauses, obligations, and conditions
    input: structured list of policy clauses
    output: summarized policy text with all clause references preserved
    error_handling: If any clause is missing, conditions are dropped, or meaning is altered, refuse output and return error