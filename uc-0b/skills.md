# skills.md

skills:

- name: retrieve_policy
  description: Loads a .txt policy file and extracts its structured numbered sections accurately.
  input: File path (string)
  output: A dictionary mapping clause numbers (e.g., "5.2") to their text content.
  error_handling: Return an empty dictionary or raise a file not found error if the input does not exist.

- name: summarize_policy
  description: Takes structured sections and produces a compliant summary without dropping conditions.
  input: Dictionary of numbered clauses and their text.
  output: A single string containing the compliant summary with all explicit clause references.
  error_handling: Refuse to summarize and output the text verbatim if loss of meaning is detected.
