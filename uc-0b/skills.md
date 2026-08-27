# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

- name: retrieve_policy
  description: "Loads the HR leave policy .txt file and returns its content as structured numbered sections and clauses."
  input: "Local filesystem path string to a .txt policy file, expected format: ../data/policy-documents/policy_hr_leave.txt."
  output: "Structured object containing ordered sections and numbered clauses, with each clause represented by clause_id, section_title, original_text, and binding terms where identifiable."
  error_handling: "Fail with a clear error if the file is missing, unreadable, empty, not a .txt file, or contains no numbered clauses; preserve original clause text when structure is ambiguous rather than guessing."

- name: summarize_policy
  description: "Takes structured policy sections and produces a compliant clause-referenced summary without changing meaning."
  input: "Structured policy object from retrieve_policy containing ordered numbered clauses and original clause text."
  output: "Plain-text summary written for uc-0b/summary_hr_leave.txt, with every numbered clause referenced and all obligations, conditions, approvers, limits, exclusions, and consequences preserved."
  error_handling: "Refuse or flag the output if any numbered clause is omitted, any multi-condition obligation loses a condition, unsupported source-external information is introduced, or a clause cannot be summarized without meaning loss; quote such clauses verbatim and flag them."
