# skills.md — UC-0B HR Leave Policy Summarizer
# Generated from the RICE prompt and refined against app.py.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections and clauses.
    input: input_path (path to policy_hr_leave.txt).
    output: tuple of metadata dict, ordered section list with clause ids, and clause_id-to-verbatim-text dict.
    error_handling: A file with no numbered clauses raises a clear refusal error instead of returning an empty or guessed summary.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary with clause references, verbatim quotes for the required clauses and a compliance checklist.
    input: metadata dict, sections list, clauses dict.
    output: multi-line string written to summary_hr_leave.txt.
    error_handling: A clause without a prepared restatement is quoted verbatim and flagged; a missing required clause is reported in the checklist rather than silently dropped.