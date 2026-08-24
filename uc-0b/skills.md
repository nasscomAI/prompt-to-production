skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured numbered sections.
    input:
      type: file_path
      format: "string — absolute or relative path to a .txt policy document (e.g., '../data/policy-documents/policy_hr_leave.txt')"
    output:
      type: structured_sections
      format: "JSON object with keys as section numbers (e.g., '2.3', '5.2') and values as clause text strings preserving binding verbs and all conditions"
    error_handling:
      - If file does not exist: raise FileNotFoundError with path
      - If file is not .txt extension: raise ValueError
      - If sections cannot be parsed into numbered clauses: return raw content with parse_warning flag

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all 10 mapped clauses with every condition intact.
    input:
      type: structured_sections
      format: "JSON object from retrieve_policy output with numbered clause keys and full clause text values"
    output:
      type: summary_text
      format: "Plain text file written to uc-0b/summary_hr_leave.txt containing all 10 clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) with multi-condition obligations fully preserved; verbatim quotes flagged where summarisation loses meaning"
    error_handling:
      - If any of the 10 required clauses are missing from input: raise ValueError listing missing clause numbers
      - If multi-condition obligation (e.g., 5.2 dual approver) detected with dropped conditions: halt and return condition_drop_error with clause number
      - If output contains phrases not in source ("standard practice", "typically", "generally expected"): raise ScopeBleedError with offending phrase
      - If clause cannot be summarised without meaning loss: quote verbatim in output and append "[VERBATIM — summarisation loses meaning]" flag