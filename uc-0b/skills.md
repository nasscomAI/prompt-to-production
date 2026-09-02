skills:
  - name: retrieve_policy
    description: Load the policy text file and return content as structured numbered sections.
    input: Path to policy text file (e.g., ../data/policy-documents/policy_hr_leave.txt)
    output: >
      JSON object with `sections` (array of objects containing clause_number and text)
      and `raw_text` (complete original document text).
    error_handling: Return refusal template if file is missing or unreadable.

  - name: summarize_policy
    description: Take structured policy sections and produce a compliant summary preserving all enforcement rules.
    input: JSON object from retrieve_policy output
    output: Plain text summary file content formatted per rules.
    error_handling: Return refusal template if input is invalid or missing required keys.