- name: retrieve_policy
  description: >
    Loads the HR leave policy text file and parses it into structured numbered clauses.
  input:
    type: string
    format: file path to a .txt policy document
  output:
    type: list
    format: list of objects containing clause number and clause text
  error_handling: >
    If the file path is invalid or the file cannot be read, return an error.
    If the document does not contain clearly identifiable numbered clauses, return an error indicating invalid structure.

- name: summarize_policy
  description: >
    Generates a legally faithful summary of the policy while preserving all clauses, obligations, and conditions.
  input:
    type: list
    format: structured list of numbered clauses with text
  output:
    type: string
    format: structured summary including all clause numbers and their obligations
  error_handling: >
    If any clause is missing, incomplete, or cannot be summarised without meaning loss, include the clause verbatim and flag it.
    If multi-condition obligations are detected, ensure all conditions are preserved; otherwise return an error.
    If the input contains ambiguous or incomplete data, refuse to summarise and return an error.
    If any attempt is made to add external or assumed information, reject and return an error.