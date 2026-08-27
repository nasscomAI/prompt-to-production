# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: String representing the relative file path (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: Structured data (e.g., JSON or mapping) representing numbered sections and their corresponding verbatim text.
    error_handling: Return an explicit error if the file cannot be accessed or if the text cannot be reliably mapped to numbered clauses. Refuse to guess.

  - name: summarize_policy
    description: Takes structured sections and produces a legally compliant summary with clause references.
    input: Structured numbered sections provided by the `retrieve_policy` skill.
    output: A verifiable text summary of the policy (e.g., to be saved as `summary_hr_leave.txt`) that retains all original clauses and multi-condition obligations.
    error_handling: If a clause cannot be accurately summarized without altering its meaning or dropping a condition, quote the clause verbatim and flag it.
