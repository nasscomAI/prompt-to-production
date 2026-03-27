skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path of the policy document (string).
    output: Parsed document content organized by structured numbered sections (dictionary or list of strings).
    error_handling: If the file is not found or cannot be read, raise a FileNotFoundError or ValueError with a clear message indicating the file access issue.

  - name: summarize_policy
    description: Takes structured sections from a policy document and produces a compliant summary with clause references strictly adhering to the enforcement rules.
    input: Structured numbered sections of the policy (dictionary or list of strings).
    output: A plain text summary of the policy preserving all conditions and meanings (string).
    error_handling: If the structured sections are empty or unparseable, return an error message indicating that the input data is insufficient for summarization.
