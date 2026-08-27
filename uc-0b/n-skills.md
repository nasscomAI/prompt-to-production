- name: retrieve_policy
  description: Loads a policy documents from the local filesystem and parses 'policy_hr_leave.txt' into structured, numbered sections for precise auditing.
  input: String representing the absolute path to the policy .txt file.
  output: List of Objects, each containing the 'clause' number and the 'content' string for each numbered section.
  error_handling: Prevents 'Clause omission' by raising a fatal error if 'policy_hr_leave.txt' is missing or if any of the 10 mandatory ground-truth clauses (2.3–7.2) cannot be identified in the source text.

- name: summarize_policy
  description: Synthesizes structured policy sections into a compliant summary while strictly preserving all original conditions, deadlines, and multi-approver requirements.
  input: List of structured Objects containing clause-numbered policy sections.
  output: List of summary bullets as Strings, each including a mandatory reference to the source clause number.
  error_handling: Mitigates 'Obligation softening' by rejecting any summary that modifies binding verbs (e.g., must, will, requires); blocks 'Scope bleed' by explicitly filtering out external phrases like 'standard practice' or 'typically'; refuses to produce output if any multi-condition obligation is simplified.
