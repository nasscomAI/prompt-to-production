# skills.md — UC-0B Skills Definition

skills:
  - name: retrieve_policy
    description: Reads raw policy text file and parses content into structured numbered sections and clauses.
    input: String file_path pointing to a policy text file (e.g. policy_hr_leave.txt).
    output: Dictionary mapping section headings and clause numbers (e.g. "2.3", "5.2") to raw clause text lines.
    error_handling: Raises FileNotFoundError if file is missing, or handles malformed section headers by treating text line-by-line.

  - name: summarize_policy
    description: Generates a complete policy summary that preserves every numbered clause, retains binding verbs and multi-condition rules, and avoids scope bleed.
    input: Structured policy dictionary returned by retrieve_policy.
    output: Formatted string containing the complete section-by-section policy summary.
    error_handling: Quotes clauses verbatim and flags them if condensation risks dropping multi-condition requirements or legal meaning.

