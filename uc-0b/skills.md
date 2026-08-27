skills:
  - name: retrieve_policy
    description: Reads and loads the HR policy document from a file.
    input: File path as a string (e.g., "../data/policy-documents/policy_hr_leave.txt")
    output: Raw policy text as a string
    error_handling: Returns an error if the file path is invalid, file is missing, or content is empty; does not proceed further.

  - name: summarize_policy
    description: Generates a concise summary of the HR policy while preserving all obligations and conditions.
    input: Raw policy text as a string
    output: Summary text as a string
    error_handling: Refuses to generate a summary if input text is empty, incomplete, or ambiguous; ensures no clause omission, no added information, and no condition dropping.