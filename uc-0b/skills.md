# skills.md

skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and returns its content as structured numbered sections.
    input: `--input` path to a policy .txt file (e.g. policy_hr_leave.txt).
    output: list of dicts, each with keys `clause_id` (e.g. "2.6") and `text` (that clause's full text).
    error_handling: If file is missing or contains no numbered clauses, raise a clear error naming the file — do not proceed to summarization with empty input.

  - name: summarize_policy
    description: Produces a clause-referenced summary from structured policy sections, preserving all conditions.
    input: list of clause dicts from retrieve_policy.
    output: string — the summary text, with every clause id referenced and multi-condition clauses fully preserved; written to `--output` path (e.g. summary_hr_leave.txt).
    error_handling: If a clause cannot be condensed without dropping a condition, include it verbatim in the summary with a "[VERBATIM — flagged]" marker instead of silently paraphrasing.
