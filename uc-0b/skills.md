skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections, preserving all original clauses.
    input: File path string to the policy document (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: Structured representation (e.g., text or JSON object) containing every numbered section and its literal text.
    error_handling: Return a specific error if the file cannot be accessed or safely parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with exact clause references, without softening obligations or omitting conditions.
    input: Structured numbered clauses/sections from retrieve_policy.
    output: A generated text summary (e.g., summary_hr_leave.txt) where all core obligations, binding verbs (must, will, requires), and multi-conditions are 100% preserved.
    error_handling: Halt execution and throw an error, falling back to quoting the text verbatim and flagging it, if any clause cannot be confidently summarized without meaning loss.
