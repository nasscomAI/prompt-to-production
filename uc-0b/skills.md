- name: retrieve_policy
  description: Loads the HR policy text file and returns structured numbered sections.
  input:
    type: string
    format: file path to .txt policy document
  output:
    type: list
    format: structured numbered clauses with section identifiers
  error_handling:
    - If file path is invalid, return error "Input file not found"
    - If file is empty, return error "Policy document is empty"
    - If clauses are not properly structured, flag as "Invalid policy format"

- name: summarize_policy
  description: Generates a compliant summary preserving all clauses and obligations.
  input:
    type: list
    format: structured numbered clauses
  output:
    type: string
    format: summary text with all clause references and preserved conditions
  error_handling:
    - If any clause is missing, return error "Clause omission detected"
    - If multi-condition obligations are reduced, return error "Condition drop detected"
    - If extra information is added, return error "Scope bleed detected"
    - If meaning changes during summarization, return error "Obligation softening detected"