# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections for easier analysis.
    input: The file path to the policy document (e.g., 'policy_hr_leave.txt').
    output: A list of numbered sections with their associated text content.
    error_handling: If the file path is invalid or empty, the skill should log an error and return an empty structure.

  - name: summarize_policy
    description: Takes structured sections from a policy document and produces a compliant summary with clause references.
    input: A structured representation of the policy (e.g., a list of numbered sections).
    output: A text summary containing references to all numbered clauses and their obligations.
    error_handling: If a clause cannot be summarized without losing detail, the entire clause is included verbatim.
