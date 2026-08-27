- name: retrieve_policy
  description: Loads a .txt policy file and returns its content as structured numbered sections.
  input: file_path (string) pointing to a .txt policy document.
  output: sections (list of objects) with clause numbers and text.
  error_handling: Raise an invalid format error if the file is unreadable or lacks numbered clauses, refusing to parse unstructured text.

- name: summarize_policy
  description: Takes structured sections and produces a compliant summary with clause references preserving all conditions and binding verbs.
  input: sections (list of objects) containing all extracted clauses from retrieve_policy.
  output: summary (string) containing a compliant summary without losing conditions or introducing scope bleed.
  error_handling: If a multi-condition requirement cannot be effectively paraphrased without modifying the meaning, explicitly quote it verbatim and flag it rather than summarizing incorrectly.
