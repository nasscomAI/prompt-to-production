skills:
  - name: retrieve_policy
    description: Loads an HR policy .txt file, parses section headers, and returns structured data with numbered sections and individual numbered clauses.
    input: File path string pointing to the policy document (e.g., policy_hr_leave.txt).
    output: Structured dictionary containing document metadata, major section headings, and a mapping of clause numbers (e.g., '2.3') to raw text.
    error_handling: Raises FileNotFoundError if the path is invalid, or ValueError if the document contains no numbered clauses.

  - name: summarize_policy
    description: Processes structured policy sections to generate a concise summary preserving every numbered clause, multi-condition approval, binding verb, and threshold without scope bleed.
    input: Structured policy dictionary produced by retrieve_policy.
    output: Formatted text summary string referencing every clause number with highlighted critical obligations and verbatim quotes for non-compressible clauses.
    error_handling: Validates that all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) and all 25 numbered clauses are present; fails with an informative error if any clause is dropped or if condition dropping occurs on Clause 5.2.
