skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content.
    input: File path of the policy document (String).
    output: Full text of the policy document (String).
    error_handling: Return error message if file cannot be read.

  - name: summarize_policy
    description: Takes the policy text, produces a compliant summary with clause references.
    input: String containing the policy text.
    output: String containing the compliant summary.
    error_handling: If input is missing or empty, return an error message.
