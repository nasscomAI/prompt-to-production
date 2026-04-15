- name: retrieve_policy
  description: Load HR policy text file and return structured clauses
  input: file path (.txt)
  output: structured text with numbered clauses
  error_handling: return error if file not found or unreadable

- name: summarize_policy
  description: Generate summary preserving all clauses and conditions
  input: structured policy text
  output: compliant summary with clause references
  error_handling: flag if any clause missing or condition dropped
