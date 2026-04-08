# skills.md

skills:

- name: summarize_policy
  description: Creates a comprehensive summary of an HR leave policy document, ensuring all numbered clauses are included and obligations are preserved without softening.
  input: File path to a text file containing the policy document.
  output: A string containing the policy summary text.
  error_handling: If the file cannot be read, return an error message; if the document lacks numbered clauses, include a note about incomplete structure.
