- name: retrieve_policy
  description: Load the policy text file and return structured numbered clauses
  input: file path to .txt policy document
  output: structured list of clauses with clause numbers and content
  error_handling: if file not found or empty, return error message

- name: summarize_policy
  description: Generate a compliant summary preserving all clauses and conditions
  input: structured policy clauses
  output: summary text with all clause references preserved
  error_handling: if clause missing or conditions unclear, flag the clause and include verbatim text