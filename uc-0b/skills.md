## Skills.md
##.
- name: retrieve_policy
  description: Loads a policy document and structures it into numbered clauses.
  input:
    type: text file
    format: .txt policy document
  output:
    type: structured data
    format: numbered clauses
  error_handling:
    - If file is missing or unreadable, raise an error
    - If clauses are not properly formatted, return raw text

- name: summarize_policy
  description: Summarizes policy clauses while preserving all obligations and conditions.
  input:
    type: structured data
    format: numbered clauses
  output:
    type: text
    format: summarized policy with all clauses preserved
  error_handling:
    - If any clause is missing, return an error
    - If conditions are dropped, regenerate summary
    - If meaning changes, quote clause verbatim and flag it