# skills.md

skills:
  - name: retrieve_policy
    description: Load the HR leave policy file and return content as structured numbered sections.
    input: "File path to policy_hr_leave.txt (string)"
    output: "Dictionary mapping section numbers to content. Example: {2.3: 'Employees must submit...', 2.4: 'Leave applications must receive...', ...}"
    error_handling: "If file not found, return error message. If file cannot be parsed, return raw content with warning. Never return empty dict."

  - name: summarize_policy
    description: Take structured policy sections and produce a summary that preserves all mandatory clauses with full conditions.
    input: "Dictionary of structured policy sections (from retrieve_policy)"
    output: "Summary text with all 10 critical clauses present, formatted clearly with clause references. Max one paragraph per clause unless marked [VERBATIM]"
    error_handling: "If a clause cannot fit summary constraints, output with [VERBATIM] marker and explanation. If any of the 10 mandatory clauses are missing, return error: 'Summary incomplete' with list of missing clauses."
