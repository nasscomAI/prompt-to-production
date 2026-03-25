skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and parses it into structured numbered clauses.
    input: File path to a .txt document containing the HR leave policy.
    output: A structured list or dictionary of clauses keyed by clause number (e.g., 2.3, 2.4, etc.) with full text.
    error_handling: If the file path is invalid or file cannot be read, return an error. If clauses cannot be identified or are missing, raise an error and do not proceed.

  - name: summarize_policy
    description: Generates a compliant summary of the HR leave policy while preserving all clauses and conditions.
    input: Structured clauses (list or dictionary) with clause numbers and their corresponding text.
    output: A text summary where each clause is represented, preserving all obligations and conditions, with clause references.
    error_handling: If any clause is missing, raise an error. If a clause contains multiple conditions and any condition may be lost, return the clause verbatim instead of summarizing. If extra information is generated that is not in the source, discard it and restrict output to source content only.