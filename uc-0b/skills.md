# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and returns structured numbered sections for deterministic clause-level processing.
    input: >
      policy_path: string path to a .txt policy file.
      File content is expected to contain numbered clauses such as 2.3, 2.4, 5.2, etc.
    output: >
      Structured object with:
      source_path,
      full_text,
      clauses as ordered list of {clause_id, clause_text},
      and missing_required_clauses list for required IDs:
      2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2.
    error_handling: >
      If file cannot be read, return a clear read error with path context.
      If numbering cannot be parsed, return raw text plus parse_warning.
      Never fabricate clauses; missing clauses must be reported explicitly.

  - name: summarize_policy
    description: Produces a compliance-safe summary from structured clauses while preserving obligations, conditions, and clause references.
    input: >
      Structured sections from retrieve_policy, including ordered clause list and any parse warnings.
    output: >
      Summary text with one entry per required clause and explicit clause references.
      Each entry preserves binding force and all conditions,
      including dual-approver requirement for clause 5.2 and >30 day escalation in 5.3.
      If a clause is high-risk to paraphrase, output verbatim text prefixed with REVIEW_REQUIRED.
    error_handling: >
      If required clauses are missing, include a completeness warning section listing missing IDs.
      If clause meaning is ambiguous, prefer verbatim quote with REVIEW_REQUIRED over paraphrase.
      Reject unsupported inferred statements that are not present in source text.
