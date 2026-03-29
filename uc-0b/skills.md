- name: retrieve_policy
  description: Reads policy document
  input: file path
  output: text
  error_handling: return error if file missing or empty

- name: summarize_policy
  description: Summarizes policy without losing meaning
  input: text
  output: summary text
  error_handling: return error if meaning is lost or clauses missing