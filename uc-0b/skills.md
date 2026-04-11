skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: String representing the policy file path (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: List of objects, each containing a clause number and the corresponding section text.
    error_handling: Returns a FileNotFoundError if the path is invalid and flags any unnumbered or malformed sections to prevent silent omission of input content.

  - name: summarize_policy
    description: Condenses structured policy sections into a compliant summary with explicit clause references and preservation of all conditions.
    input: List of objects containing clause numbers and section text.
    output: String containing a summarized policy that preserves binding verbs and includes mandatory clause references.
    error_handling: Detects and rejects summaries exhibiting clause omission, scope bleed, or obligation softening; if a multi-condition clause (e.g., Clause 5.2) cannot be condensed without dropping an approver or condition, the skill quotes the clause verbatim and flags it for meaning loss.
