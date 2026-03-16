# skills.md

skills:
  - name: retrieve_policy
    description: Load the HR leave policy document and extract numbered clauses.
    input: Path to the policy text file (policy_hr_leave.txt).
    output: Structured list of clauses with clause numbers and text.
    error_handling: If the file cannot be read or is empty, return an error message and stop processing.

  - name: summarize_policy
    description: Generate a summary of the policy while preserving the meaning of each clause.
    input: Structured list of policy clauses.
    output: Text summary referencing each clause without dropping conditions or obligations.
    error_handling: If a clause cannot be summarized safely, quote the original clause and flag it.