# UC-0B skills

skills:
  - name: retrieve_policy
    description: Load the HR leave policy text and extract numbered sections into a structured representation.
    input: |
      Path to a plain-text policy file such as `../data/policy-documents/policy_hr_leave.txt`.
    output: |
      A structured object with numbered clauses, section headings, and full clause text for each numbered item.
    error_handling: |
      - If the file cannot be read, raise a clear error.
      - If clause numbering cannot be detected, return the raw text and flag parsing failure.

  - name: summarize_policy
    description: Summarize structured policy clauses into a compliant HR leave summary while preserving all numbered obligations.
    input: |
      Structured policy clauses returned by `retrieve_policy`, including clause numbers and original text.
    output: |
      A plain-text summary file containing every numbered clause and preserving multi-condition obligations.
    error_handling: |
      - If a clause cannot be summarized without meaning loss, quote it verbatim and mark it for review.
      - Do not invent additional policy details or generalize beyond the source document.

notes: |
  - The primary skills for UC-0B are `retrieve_policy` and `summarize_policy`.
  - The summary must reflect the 10 clause inventory in README.md and preserve the conditions for clauses such as 5.2.
  - Avoid scope bleed phrases like "typically" or "generally" that are not present in the policy text.
