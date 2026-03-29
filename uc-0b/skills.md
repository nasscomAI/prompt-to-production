skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path (string) to the .txt policy document
    output: Structured numbered sections (JSON/Dict) of the policy contents
    error_handling: Return error message if file not found or document format is invalid

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections (JSON/Dict) and agents.md rules
    output: Compliant summary text (string) with all clause conditions preserved
    error_handling: Return error message if required sections are missing or unclear
