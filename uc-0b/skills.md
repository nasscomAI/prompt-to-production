# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy file from the local directory and returns it as a structured map of numbered clauses and their content.
    input: File path to a .txt policy file (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A collection of structured sections with clause numbers as keys and their associated text as values.
    error_handling: Return an error if the file path is invalid or the document does not contain recognizable clause numbers.

  - name: summarize_policy
    description: Generates a summary that preserves all multi-condition obligations and binding requirements for every input clause.
    input: Structured policy sections with clause numbers and text.
    output: A summary document that includes every numbered clause, with flagging for clauses that had to be quoted verbatim to maintain meaning integrity.
    error_handling: Refuse to process if a section is missing text; if a clause summary loses dual conditions (e.g., dual approvals), it must be flagged for manual review.
