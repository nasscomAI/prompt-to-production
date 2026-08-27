- name: retrieve_policy
  description: Load HR policy document and return structured numbered clauses.
  input: text file path
  output: list of numbered clauses (string list)
  error_handling: Return error if file missing or format invalid

- name: summarize_policy
  description: Generate summary preserving all clauses and conditions with references.
  input: list of numbered clauses
  output: structured summary text with clause numbers
  error_handling: Refuse or quote verbatim if any clause loses meaning or conditions