skills:
  - name: retrieve_policy
    description: Load the HR leave policy from a text file into a string for parsing.
    input: String path to the text file.
    output: String representing the content of the policy text file.
    error_handling: Raise an explicit error if the file cannot be found or read.

  - name: summarize_policy
    description: Parse the policy text, extract all specific clauses, and compile them into a correct summary without dropping conditions.
    input: String representing the policy content.
    output: String representing the compliant, formatted summary.
    error_handling: Return an error message summary if parsing fails or all specific clauses cannot be found.
