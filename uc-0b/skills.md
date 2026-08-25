skills:
  - name: retrieve_policy
    description: Loads the HR leave policy .txt file and returns content as structured numbered sections.
    input: >
      file_path (string) — path to policy_hr_leave.txt. File is UTF-8 plain text with numbered clauses
      (e.g., 1.1, 2.3). No other inputs accepted.
    output: >
      Ordered dict mapping clause_id (string "2.3") to clause_text (string, full original text with line-breaks collapsed),
      plus metadata dict with document_reference, version, effective_date. Preserves clause order as in source.
      Example: {"2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.", ...}
    error_handling: >
      If file not found or unreadable → raise FileNotFoundError with path. If no numbered clauses matched → raise ValueError
      "No clauses found — invalid policy file". Blank lines and decorative separators (═══) are ignored. Never synthesize clauses.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references and binding verbs preserved.
    input: >
      sections (ordered dict clause_id → clause_text) from retrieve_policy. Must contain at least the 10 critical clauses
      2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2.
    output: >
      Single plain-text string summary where every numbered clause appears as "Clause X.Y: <obligation with binding verb preserved>".
      Multi-condition clauses preserve ALL conditions. Critical clauses are quoted or near-verbatim to avoid meaning loss. No hedging or invented
      content. Includes header citing source file name and reference. Ready to write to summary_hr_leave.txt.
    error_handling: >
      If any of the 10 critical clauses missing from input → raise ValueError listing missing clauses, do not generate partial summary.
      After generation, validates that each critical clause_id appears in output and that condition keywords present
      (e.g., 5.2 contains "Department Head" AND "HR Director", 2.4 contains "written" AND "before" AND "Verbal not valid").
      If validation fails → append [VERBATIM — meaning preservation required] and quote source clause verbatim. Never silently drop a condition.
      If output contains forbidden phrases ("typically", "generally", "standard practice") → remove and raise warning.
