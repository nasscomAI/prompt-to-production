# skills.md

skills:
  - name: retrieve_policy
    description: Load the HR leave policy text and return structured numbered clauses.
    input: >
      `input_path` to a UTF-8 plain-text policy document (e.g.,
      `../data/policy-documents/policy_hr_leave.txt`).
    output: >
      A structured object containing:
      `full_text`, ordered `sections` keyed by clause number, and a clause inventory that includes
      at minimum: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2.
    error_handling: >
      If file read/parsing fails or clause numbering is incomplete, return a validation error with
      missing clause IDs and stop downstream summarization instead of guessing.

  - name: summarize_policy
    description: Generate a compliant summary from structured policy clauses with references.
    input: >
      Structured clause data from `retrieve_policy`, including numbered sections and source text.
    output: >
      A summary text where each bullet/line includes a clause reference and preserves obligations
      exactly, including all conditions (e.g., dual approvals in 5.2), thresholds (3+ days, >30
      days), time windows (14-day notice, 48 hours, Jan-Mar), and prohibitions (7.2).
      If unavoidable meaning loss exists for any clause, include that clause verbatim and add
      `NEEDS_REVIEW`.
    error_handling: >
      Reject output as invalid if any required clause is missing, if wording softens binding verbs,
      or if content not present in source text is introduced; return explicit validation failures and
      the offending clause references.
