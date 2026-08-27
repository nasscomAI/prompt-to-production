skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    inputs:
      - name: file_path
        type: string
        description: Path to the .txt policy file
    outputs:
      - name: structured_sections
        type: string
        description: Structured numbered sections of the policy

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    inputs:
      - name: structured_sections
        type: string
        description: Structured numbered sections of the policy
    outputs:
      - name: summary
        type: string
        description: Compliant summary text with clause references
