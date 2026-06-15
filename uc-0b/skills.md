skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured numbered sections.
    input: File path string pointing to a .txt policy document (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: Ordered list of sections, each containing a clause number and its full verbatim text as read from the file.
    error_handling: If the file path does not exist or is unreadable, raise an error and halt — do not proceed with empty or partial content. If a section cannot be assigned a clause number, include it as-is and flag it for manual review.

  - name: summarize_policy
    description: Takes structured numbered sections from retrieve_policy and produces a compliant summary that preserves clause references, all conditions, and binding verbs.
    input: Ordered list of numbered sections as returned by retrieve_policy.
    output: Plain-text summary where every clause is referenced by number, every multi-condition obligation lists all conditions, and binding verbs (must, will, requires, not permitted) are reproduced verbatim or stronger — never weakened.
    error_handling: If a clause cannot be summarised without dropping a condition or softening a binding verb, quote it verbatim from the source and append a flag marker (e.g. [VERBATIM — summarisation would cause meaning loss]). Never silently omit a clause; if a clause is ambiguous, flag it rather than guess.
