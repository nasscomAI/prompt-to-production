# skills.md
skills:
  - name: retrieve_policy
    description: >
      Loads the HR leave policy text file and extracts numbered clauses
      as structured sections for further processing.
    input: >
      Path to a .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A structured list of clauses where each item contains the clause number
      and its corresponding text.
    error_handling: >
      If the file cannot be found or read, return an error and stop execution
      rather than attempting to generate a summary.

  - name: summarize_policy
    description: >
      Generates a compliant summary of the policy while preserving every
      numbered clause and its binding obligations.
    input: >
      Structured policy clauses containing clause numbers and text.
    output: >
      A text summary that includes each clause reference and preserves all
      conditions and obligations present in the source document.
    error_handling: >
      If a clause cannot be summarized without losing meaning or conditions,
      include the clause verbatim in the output and mark it for review.