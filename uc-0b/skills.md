skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text and extracts structured numbered clauses for downstream validation-aware summarization.
    input: "Path to policy text file (.txt), expected: ../data/policy-documents/policy_hr_leave.txt"
    output: "Structured object/list of numbered sections with clause_id and clause_text, preserving exact wording."
    error_handling: "If file is missing/unreadable, raise a clear file error. If required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are absent, return validation failure listing missing clause IDs."

  - name: summarize_policy
    description: Produces a clause-referenced summary that preserves all obligations and conditions without adding external information.
    input: "Structured numbered sections from retrieve_policy, including required clause IDs."
    output: "Text summary with explicit clause references covering all required clauses and preserving binding meaning."
    error_handling: "If any required clause cannot be summarized without meaning loss, quote that clause verbatim and append [FLAG: VERBATIM_REQUIRED]. If any required clause is missing in input structure, fail fast with missing-clause report instead of generating partial summary."