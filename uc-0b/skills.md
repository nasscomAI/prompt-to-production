skills:
- name: retrieve_policy
  description: Load the HR leave policy text and return its numbered clauses as structured sections.
  input: Path to the policy_hr_leave.txt file.
  output: Structured numbered policy sections containing clause numbers and source text.
  error_handling: If the policy cannot be read or a required clause is unavailable, report the issue rather than inventing content.

- name: summarize_policy
  description: Produce a compliant summary of the policy while preserving all required clause conditions and obligations.
  input: Structured numbered policy sections from retrieve_policy.
  output: A clause-referenced policy summary containing all ten ground-truth clauses.
  error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it for review.
