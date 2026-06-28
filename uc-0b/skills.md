skills:
  - name: retrieve_policy
    description: Loads a policy text file and extracts numbered clauses.
    input: Policy text file path.
    output: Structured list of policy clauses.
    error_handling: Returns an error if the file is missing or cannot be read.

  - name: summarize_policy
    description: Produces a compliant summary while preserving obligations and conditions.
    input: Structured policy clauses.
    output: Summary with clause references and preserved conditions.
    error_handling: Quotes original clause text when meaning would otherwise be lost.