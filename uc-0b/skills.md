skills:

## 1) name: retrieve_policy
  - description: Reads a policy text file and extracts numbered clauses into structured sections.
  - input: File path to a .txt policy document
  - output: Dictionary mapping clause_id (string) to clause text (string)
  - error_handling: Returns empty dictionary if file cannot be read; missing clauses handled downstream

## 2) name: summarize_policy
  - description: Produces a clause-preserving summary ensuring no meaning loss or condition drop.
  - input: Dictionary of clause_id to clause text
  - output: Formatted text summary with clause numbers and content
  - error_handling: Missing clauses are marked as [MISSING — NEEDS_REVIEW]; risky clauses are flagged with [REVIEW]
