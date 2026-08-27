# skills.md

skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: path to policy_hr_leave.txt
    output: structured numbered sections
    error_handling: Return error if the file cannot be accessed

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: structured numbered sections
    output: compliant summary with clause references
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it
