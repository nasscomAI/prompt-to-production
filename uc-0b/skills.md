skills:
  - name: retrieve_policy
    description: Reads the raw policy text file and parses it into structured numbered sections and clauses.
    input: File path string pointing to the policy document (e.g. data/policy-documents/policy_hr_leave.txt).
    output: Data structure containing header metadata and dictionary of numbered clause sections with full clause text.
    error_handling: Raises file not found error if file path is invalid, or reports empty document if content cannot be parsed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a complete, non-lossy summary retaining 100% of binding clauses and conditions.
    input: Structured policy sections dictionary produced by retrieve_policy.
    output: Formatted text string containing section-by-section and clause-by-clause obligation summary.
    error_handling: If a clause contains multi-condition rules or cannot be compressed without risking obligation softening, quotes the clause verbatim.
