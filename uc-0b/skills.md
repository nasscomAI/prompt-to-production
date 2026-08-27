# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections.
    input: File path (string) to a .txt policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: Dictionary with keys as section numbers (e.g., "2.3", "5.2") and values as the raw text of each clause.
    error_handling: If the file is missing, malformed, or contains no numbered clauses, return `{"error": "Invalid policy file"}` and refuse to proceed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Dictionary of structured sections (from `retrieve_policy`) and the ground truth clauses (from README).
    output: String containing the summary, with each clause explicitly referenced (e.g., "[2.3] 14-day advance notice required"). Non-summarizable clauses are quoted verbatim and flagged.
    error_handling: If a clause cannot be matched or summarized without meaning loss, return the verbatim text with a `[VERBATIM: <clause_number>]` flag and log a warning.
