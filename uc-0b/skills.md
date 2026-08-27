- name: retrieve_policy
  description: >
    Loads a policy text file and converts it into structured numbered sections.
  input:
    type: string
    format: file path to a .txt policy document
  output:
    type: list
    format: list of objects with clause number and corresponding text
  error_handling:
    - "If file path is invalid or file cannot be read, return an error."
    - "If document is empty or not properly structured, return an error."
    - "Do not attempt to infer or fabricate missing clauses."

- name: summarize_policy
  description: >
    Generates a clause-preserving summary from structured policy sections.
  input:
    type: list
    format: structured list of clauses with clause numbers and text
  output:
    type: string
    format: summarized policy text with all clauses referenced
  error_handling:
    - "If any clause is missing from input, reject the summarization."
    - "If a clause contains multiple conditions, ensure all are preserved in output."
    - "If summarization causes meaning loss, quote the clause verbatim and flag it."
    - "Do not add any information not present in the input."
    - "If ambiguity is detected, return an error instead of guessing."