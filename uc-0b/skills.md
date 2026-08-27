- name: retrieve_policy
  description: Reads and retrieves the HR policy document from the given file path
  input: "File path to the HR policy document as a string"
  output: "Full text content of the policy document"
  error_handling: >
    If the file does not exist or cannot be read, return an error message and stop execution.

- name: summarize_policy
  description: Generates a summary of the HR policy document preserving all obligations and conditions
  input: "Full text of the HR policy document"
  output: "A summarized version of the policy document maintaining all clauses"
  error_handling: >
    If the input text is empty or ambiguous, return a refusal message.
    If summarization risks losing clauses or conditions, do not summarize and return a refusal.