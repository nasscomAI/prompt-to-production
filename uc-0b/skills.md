# skills.md

skills:
- name: retrieve_policy
  description: Loads a .txt policy file and extracts the content into structured numbered sections for precise clause mapping.
  input:
    type: string
    format: File path to the source .txt policy document (e.g., '../data/policy-documents/policy_hr_leave.txt').
  output:
    type: array
    format: A list of objects containing clause numbers (e.g., "5.2") and their corresponding raw text.
  error_handling: >
    Raises an error if the file path is invalid, inaccessible, or the document contains no identifiable numbered clauses. If a section is ambiguous or fails to parse, it returns the raw segment with a 'parsing_error' flag.

- name: summarize_policy
  description: Produces a compliant summary from structured sections while strictly adhering to binding verbs and condition preservation for all mandatory clauses.
  input:
    type: array
    format: Structured list of policy clauses from the retrieve_policy skill.
  output:
    type: string
    format: A summary document with explicit clause references (e.g., [2.3]) and preserved multi-part obligations.
  error_handling: >
    Validates output against the 10-clause ground truth; raises 'Clause Omission' if any are missing. Triggers a 'Condition Drop' error if multi-condition obligations (specifically 5.2) are simplified. Rejects output if 'Scope Bleed' (external practices or organizational assumptions) is detected. If a clause cannot be summarized without loss of meaning, it quotes the source verbatim and flags it for manual review.
