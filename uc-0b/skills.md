- name: retrieve_policy
  description: >
    Retrieves the full text of the HR leave policy document for summarization.
  input:
    type: string
    format: "File path to the HR leave policy text file"
  output:
    type: string
    format: "Content of the policy document as text"
  error_handling: >
    If the file is missing, unreadable, or empty, raise an error and do not proceed with summarization.

- name: summarize_policy
  description: >
    Generates a concise summary of the HR leave policy while preserving all clauses and multi-condition obligations.
  input:
    type: string
    format: "Text content of the HR leave policy document"
  output:
    type: string
    format: "Summary text preserving all obligations, clauses, and conditions"
  error_handling: >
    If the input text is ambiguous or violates the enforcement rules, refuse to summarize and provide an explicit error message.