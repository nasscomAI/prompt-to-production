skills:

* name: retrieve_policy
  description: Loads a policy document text file and returns its content.
  input: Path to a .txt policy file.
  output: String containing the entire policy text.
  error_handling: If the file cannot be opened, return an error message.

* name: summarize_policy
  description: Generates a structured summary preserving every clause and obligation.
  input: Policy document text.
  output: Text summary with clause numbers and obligations preserved.
  error_handling: If clauses cannot be parsed, quote the clause verbatim and flag it.
