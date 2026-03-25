- name: retrieve_policy
  description: Retrieve HR policy text from input file
  input: file path (text file)
  output: full text content of the policy
  error_handling: Return error if file not found or empty

- name: summarize_policy
  description: Generate summary preserving all obligations and clauses
  input: policy text string
  output: summarized policy text
  error_handling: Refuse if any clause may be omitted or meaning altered