- name: retrieve_policy
  description: Loads a .txt policy file and returns the content as structured numbered sections.
  input: 
    type: string
    format: file path (e.g., "../data/policy-documents/policy_hr_leave.txt")
  output: 
    type: object
    format: structured JSON mapping clause numbers to their exact text strings
  error_handling: If the file cannot be found or read, immediately return an error stating the document is inaccessible rather than attempting to guess the policy.

- name: summarize_policy
  description: Takes structured sections and produces a compliant summary with clause references.
  input: 
    type: object
    format: structured JSON containing policy clauses
  output: 
    type: string
    format: formatted text summary referencing clause numbers
  error_handling: If summarizing a specific clause would result in clause omission, scope bleed, or condition dropping (such as omitting one of multiple required approvers), the skill must abort summarizing that specific clause, output it verbatim, and flag it as un-summarizable.