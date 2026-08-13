# skills.md — UC-0B Policy Summarizer Skills

skills:
  - name: retrieve_policy
    description: Reads a raw policy text file (.txt), parses section headers and numbered clause items, and returns a structured mapping of clause numbers to clause text.
    input: File path string pointing to the policy text file (e.g. policy_hr_leave.txt).
    output: Dictionary mapping section headings and clause numbers (e.g., '2.3', '5.2') to text strings.
    error_handling: Raises FileNotFoundError if file is missing, or returns empty mapping with error flag if unreadable.

  - name: summarize_policy
    description: Takes structured policy clauses and produces a comprehensive summary preserving all 10 core clauses, multi-approver requirements, binding modal verbs, and verbatim quotes for delicate clauses.
    input: Structured dictionary of policy sections and clause mappings.
    output: String formatted policy summary text containing all section summaries and clause references.
    error_handling: Flags missing or unparseable clauses explicitly rather than omitting them from the final summary text.
