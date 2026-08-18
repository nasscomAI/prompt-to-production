# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a .txt policy file (string), e.g. ../data/policy-documents/policy_hr_leave.txt.
    output: Structured numbered sections (map of clause number -> clause text), preserving the original wording exactly.
    error_handling: If the file is missing, unreadable, or contains no numbered clauses, refuse to proceed and report the error rather than fabricating content.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references that preserves every obligation, condition, and binding verb.
    input: Structured numbered sections from retrieve_policy (map of clause number -> clause text).
    output: Summary text where every numbered clause is present and referenced by its clause number, all conditions are kept, and binding strength is unchanged.
    error_handling: If a clause cannot be summarised without losing meaning, quote it verbatim and flag it — never guess or soften the obligation. If the input sections lack any of the expected clauses, refuse to produce the summary and report which clauses are missing.
