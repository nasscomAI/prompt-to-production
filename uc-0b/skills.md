# skills.md — UC-0B Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: Reads a raw text policy document and parses its contents into structured, numbered sections.
    input: The file path to the raw text policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: A structured object (like a dictionary or list) mapping clause numbers (e.g., "2.3") to their corresponding exact text.
    error_handling: Throws a file parsing error if the document is unreadable or if it lacks standard numbered clause formatting.

  - name: summarize_policy
    description: Generates a highly accurate, compliant summary from structured policy sections, preserving all obligations, conditions, and clause references.
    input: The structured object of numbered clauses outputted by `retrieve_policy`.
    output: A comprehensive text string containing the summarized policy document.
    error_handling: Automatically outputs the original text verbatim and prepends `[VERBATIM_REQUIRED]` if a specific clause's logic is too complex to summarize without risking meaning loss or condition dropping.
