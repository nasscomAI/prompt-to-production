skills:
  - name: retrieve_policy
    description: Loads the designated HR policy .txt file and returns its content as logically structured numbered sections.
    input: File path (string, e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: Structured sections and clauses (JSON or comparable structured format).
    error_handling: If the file is missing, unreadable, or empty, halt execution and raise a clear file-not-found or read error to prevent hallucination.

  - name: summarize_policy
    description: Takes structured clauses and produces a strictly compliant summary with explicit clause references, preventing any scope bleed, clause omission, or obligation softening.
    input: Structured numbered sections (JSON or similar structured data).
    output: Formatted text summary where every numbered clause, condition, and binding verb is fully preserved and accurate.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it. Refuse to guess or continue if clauses are unreadable or require external context.
