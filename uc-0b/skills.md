skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and converts it into structured numbered clauses.
    input: file path to a .txt policy document
    output: list of structured clauses with clause numbers and text
    error_handling: returns an error if file path is invalid, file is empty, or structure cannot be parsed correctly

  - name: summarize_policy
    description: Generates a compliant summary preserving all clauses and conditions.
    input: list of structured clauses with clause numbers and text
    output: summarized policy text with clause references
    error_handling: ensures no clause is missing, preserves all conditions, and returns verbatim clauses if meaning may change