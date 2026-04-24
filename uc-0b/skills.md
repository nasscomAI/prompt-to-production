# skills.md
skills:
  - name: retrieve_policy
    description: Loads HR policy .txt file, returns content as structured sections with numbered clauses
    input: Path to policy_hr_leave.txt
    output: Dictionary of {section_number: {"clauses": {clause_id: text}}}
    error_handling: Raise ValueError if file not found or not valid policy format

  - name: summarize_policy
    description: Takes structured policy sections, produces summary with clause references preserved
    input: Structured policy dictionary from retrieve_policy
    output: summary_hr_leave.txt with all 10 clauses covered
    error_handling: If clause cannot be summarised without meaning loss, include verbatim with [QUOTE] tag