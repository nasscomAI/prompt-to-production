- name: retrieve_policy
  description: Loads a .txt policy file and returns its content as structured numbered sections.
  input: File path (string) to a .txt policy document.
  output: Structured text with each policy clause extracted as a numbered section (e.g., "2.3", "2.4", etc.).
  error_handling: If the file does not exist or is not a .txt file, return an error. If empty, return a warning.

- name: summarize_policy
  description: Takes structured policy sections and produces a compliant summary referencing every clause in the inventory, preserving all conditions and binding verbs.
  input: Structured policy sections (output of retrieve_policy).
  output: Compliant summary text that references all 10 numbered clauses (2.3–7.2), preserves multi-condition obligations fully, and contains no information absent from the source document.
  error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it. If input is empty, return an empty summary.
