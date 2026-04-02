skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections
    input: File path to the .txt policy document (string)
    output: Structured numbered sections of the policy document (array of objects or structured string)
    error_handling: Refuse to proceed and return an error if the file cannot be found or read

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections of the policy
    output: A compliant summary text with clause references (string)
    error_handling: If input sections are invalid, return an error indicating the format is incorrect and refuse to summarize
