- name: retrieve_policy
  description: Loads the .txt policy file and returns the content as structured numbered sections.
  input:
    type: string
    format: File path to the .txt policy document
  output:
    type: list of objects
    format: Each object contains a 'section_number' and 'content'.
  error_handling: Return an error if the file cannot be found or read.

- name: summarize_policy
  description: Takes structured sections and produces a compliant summary with clause references strictly adhering to enforcement rules.
  input:
    type: list of objects
    format: Outputs from retrieve_policy, containing 'section_number' and 'content'.
  output:
    type: string
    format: A formatted text summary containing all required clauses and preserved conditions.
  error_handling: If a clause cannot be summarized without meaning loss or scope bleed/condition dropping is detected, quote the clause verbatim and flag it with a warning.
