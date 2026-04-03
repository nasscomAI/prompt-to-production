skills:
  - name: retrieve_policy
    description: Loads HR policy .txt file, returns content as structured numbered sections
    input: str - path to policy_hr_leave.txt file
    output: dict - sections keyed by clause number with content preserved
    error_handling: If file cannot be read, raise FileNotFoundError with clear message

  - name: summarize_policy
    description: Takes structured policy sections, produces compliant summary with clause references
    input: dict - structured sections from retrieve_policy
    output: str - summary text with all 10 clauses preserved, binding verbs exact
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and mark with [QUOTE] tag