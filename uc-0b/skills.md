skills:

- name: summarize_document
  description: Generates a concise summary while preserving the original meaning.
  input: A document or text string.
  output: A summarized version of the document.
  error_handling: If the document is empty or unclear, return an appropriate message instead of guessing.

- name: validate_summary
  description: Checks whether the summary accurately reflects the original document.
  input: Original document and generated summary.
  output: Validation result indicating whether important information is preserved.
  error_handling: If either input is missing, return a validation error.
