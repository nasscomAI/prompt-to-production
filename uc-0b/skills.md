# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) pointing to the policy document.
    output: Structured text or JSON array mapping clause numbers to their exact text.
    error_handling: Return a descriptive error if the file is missing, unreadable, or empty.

  - name: summarize_policy
    description: Takes structured sections of a policy and produces a compliant summary with clause references.
    input: Structured policy sections (text or JSON) from retrieve_policy.
    output: Formatted summary string preserving all conditions and obligations without hallucination.
    error_handling: If a clause cannot be summarized without losing meaning or conditions, quote it verbatim, flag it, and continue.
