skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: file path
    output: string
    error_handling: handle errors
  - name: summarize_policy
    description: takes structured sections, produces compliant summary
    input: text
    output: summary text
    error_handling: handle errors
