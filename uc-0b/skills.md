skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and extracts a structured clause inventory keyed by numbered sections.
    input: "String file path to a plain-text policy document (for UC-0B: ../data/policy-documents/policy_hr_leave.txt)."
    output: "JSON object with raw_text:string and clauses:array where each clause has clause_id:string, text:string, binding_verbs:array, and conditions:array."
    error_handling: "If file is missing, unreadable, or malformed, return a structured error with reason and stop downstream summarization. If numbered clauses are partially parsed, return parsed clauses plus warning: INCOMPLETE_PARSE and flag: NEEDS_REVIEW."

  - name: summarize_policy
    description: Produces a faithful summary from structured clauses while preserving all obligations and conditions.
    input: "Structured policy object from retrieve_policy containing numbered clauses and clause text."
    output: "Text summary with explicit clause references covering 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2; includes verbatim quote for any clause that cannot be safely compressed and optional flag NEEDS_REVIEW."
    error_handling: "If any required clause is missing, or a multi-condition rule cannot be preserved, do not guess; emit an incomplete summary with missing_clause_ids list and flag: NEEDS_REVIEW. If potential scope bleed is detected, remove non-source statements before returning output."
