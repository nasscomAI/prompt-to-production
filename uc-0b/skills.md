skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and converts it into structured numbered clauses for downstream compliance-safe summarization.
    input: >
      Object with `input_path` (string, relative or absolute path to a .txt policy file,
      for UC-0B expected `../data/policy-documents/policy_hr_leave.txt`).
    output: >
      Object with `document_title` (string), `clauses` (array of objects: `id` string,
      `text` string, `binding_terms` array[string]), and `source_path` (string).
      Clauses must preserve original numbering (for UC-0B, includes 2.3, 2.4, 2.5,
      2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 when present in source).
    error_handling: >
      If path is missing, unreadable, non-.txt, or file has no parseable numbered
      clauses, return `status: error` with machine-readable `code` and human-readable
      `message`; do not infer or fabricate missing clause text.

  - name: summarize_policy
    description: Produces a clause-faithful summary from structured clauses while preserving obligations, conditions, and clause references.
    input: >
      Object with `clauses` (array from retrieve_policy), `strict_mode` (boolean,
      default true), and optional `required_clause_ids` (array[string]).
    output: >
      Object with `summary_lines` (array of strings formatted as
      "[clause_id] <summary>"), `coverage_report` (object with `present`, `missing`,
      `verbatim_required` arrays), and `compliance` (object with booleans:
      `all_clauses_present`, `all_conditions_preserved`, `no_added_information`).
      Summary must retain all multi-condition requirements (for example, clause 5.2
      must include approval from both Department Head and HR Director).
    error_handling: >
      If any required clause is missing, clause text is ambiguous, or summarization
      would lose meaning, return `status: error` or mark affected entries as
      `VERBATIM_REQUIRED` with the original clause quoted; refuse instead of guessing
      and do not insert external assumptions.
