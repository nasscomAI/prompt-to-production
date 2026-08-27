# skills.md

skills:

- name: summarize_policy
  description: Generates a concise summary of a policy document while preserving all important clauses and conditions.
  input: Policy document text file (plain text).
  output: A structured summary text that includes the key clauses and requirements.
  error_handling: If a clause is unclear, keep the original wording in the summary instead of guessing.

- name: preserve_clause_conditions
  description: Ensures that approval requirements, exceptions, and conditions from each clause remain in the summary.
  input: Individual clause text extracted from the policy document.
  output: A summarized clause that still contains all required conditions and approvals.
  error_handling: If the meaning of a clause may change during summarization, return the original clause unchanged.