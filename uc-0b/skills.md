- name: retrieve_policy
  description: Loads the HR leave policy text file and returns structured numbered sections.
  input:
    type: string
    format: file path to .txt policy document
  output:
    type: list
    format: list of sections with clause numbers and corresponding text
  error_handling:
    - If file path is invalid, return an error message.
    - If file is empty or unreadable, return an error.
    - If clauses cannot be identified, return partial sections with warning.

- name: summarize_policy
  description: Generates a clause-complete summary preserving all obligations and conditions.
  input:
    type: list
    format: structured sections with clause numbers and text
  output:
    type: string
    format: summary text including all clauses with preserved conditions
  error_handling:
    - If any clause is missing, return an error.
    - If a condition is dropped, reject output and flag issue.
    - If summarization risks meaning loss, quote the clause verbatim.
    - If extra information is detected, remove it and warn.