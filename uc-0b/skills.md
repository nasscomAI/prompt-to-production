skills:

- name: retrieve_policy
  description: Loads a .txt policy file and returns the content parsed as structured numbered sections to prevent omission.
  input: File path string pointing to the text document.
  output: A dictionary mapping section headings to a list of parsed, numbered clauses.
  error_handling: Return an error if the policy text file is unreadable or malformed, and output raw text if structured extraction fails.

- name: summarize_policy
  description: Takes structured document sections and produces a compliant, concise summary ensuring all necessary conditions and clause references are preserved.
  input: Dictionary of structured policy sections from retrieve_policy.
  output: A formatted markdown text string of the summary without any scope bleed.
  error_handling: If a multi-condition clause cannot be safely summarized without meaning loss, keep and output the exact verbatim text of that clause as the summary item.
