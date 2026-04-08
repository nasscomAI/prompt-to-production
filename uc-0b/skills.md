skills:

* name: retrieve_policy
  description: Reads the policy text file and extracts numbered clauses as structured sections.
  input: Path to a .txt policy document.
  output: A list of clauses where each clause contains clause_number and clause_text.
  error_handling: If the file cannot be read, return an empty list and log an error.

* name: summarize_policy
  description: Generates a summary that preserves the meaning of each policy clause.
  input: Structured list of policy clauses from retrieve_policy.
  output: Text summary referencing each clause number.
  error_handling: If a clause cannot be safely summarized, output the original clause text and flag it.
