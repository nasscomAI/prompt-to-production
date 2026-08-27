skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and returns structured numbered clauses.
    input: File path to a .txt policy document.
    output: Structured list of numbered policy clauses.
    error_handling: Returns an error if file is missing or content cannot be parsed.

  - name: summarize_policy
    description: Produces a clause-by-clause summary preserving all obligations and conditions.
    input: Structured policy clauses.
    output: Summary text with all clauses and conditions preserved.
    error_handling: Returns an error if any clause is missing or conditions are dropped.