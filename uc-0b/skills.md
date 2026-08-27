# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections and clauses.
    input: A filesystem path (str) to a UTF-8 policy .txt file structured with "N. SECTION TITLE" headers and "N.N clause text" clauses.
    output: A list of section dicts, each {"number": str, "title": str, "clauses": [{"id": str, "text": str}]}. Multi-line clauses are joined into one whitespace-normalized string; box-drawing rules and blank lines are ignored.
    error_handling: Raises FileNotFoundError if the path does not exist. Lines before the first section header, and continuation lines with no active clause, are ignored rather than misattributed.

  - name: summarize_policy
    description: Builds a compliant, extractive summary from structured sections — every clause preserved, binding verbs kept, multi-condition clauses flagged.
    input: The list of section dicts returned by retrieve_policy.
    output: A tuple (summary_text: str, all_clause_ids: list[str], multi_condition_ids: list[str]). Each summary line carries the clause id, its binding verb, and a [MULTI-CONDITION] marker where applicable.
    error_handling: Content is copied verbatim from source clauses, so it cannot add or drop information. The paired enforcement check raises AssertionError on any missing clause, a dropped condition in clause 5.2, or an introduced scope-bleed phrase — before any output is written.
