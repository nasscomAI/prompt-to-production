skills:
  - name: "retrieve_policy"
    description: "Loads the .txt policy file and returns the content as structured numbered sections."
    input:
      type: "string"
      format: "file path (e.g., '../data/policy-documents/policy_hr_leave.txt')"
    output:
      type: "list"
      format: "structured blocks of text parsed by numbered clause sections"
    error_handling:
      - "If the file is unreadable or empty, explicitly abort the operation and return an 'Unknown/Invalid File' error."
      - "If the structure cannot be parsed into numbered sections, refuse to process and flag as malformed rather than hallucinating sections."

  - name: "summarize_policy"
    description: "Takes structured sections and produces a compliant summary with clause references."
    input:
      type: "list"
      format: "structured numbered sections output from retrieve_policy"
    output:
      type: "string"
      format: "compliant summary document mapping core obligations, binding verbs, and explicit clause numbers"
    error_handling:
      - "Clause omission: Check if any input numbered clauses are missing in the generated summary. If omitted, trigger a validation error."
      - "Scope bleed: If the summary contains external phrases like 'as is standard practice' or general expectations not in the strict input text, reject and regenerate."
      - "Obligation softening / Condition dropping: If binding verbs are weakened (e.g., 'must' becomes 'should') or if multi-condition approvers (like requiring BOTH Department Head AND HR Director) are partially dropped, immediately flag and fail the process."
