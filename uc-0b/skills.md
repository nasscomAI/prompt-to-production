# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return it as structured numbered sections and clauses.
    input: input_path to the policy .txt file.
    output: >
      A dict with `sections` ({section_number: title}), `clauses`
      ({clause_id: full whitespace-normalised clause text}), and `clause_order`
      (clause ids in reading order). Wrapped lines are rejoined per clause.
    error_handling: >
      Skips blank/divider lines. A clause missing from source simply won't appear
      in `clauses`, which the summariser detects and flags downstream.

  - name: summarize_policy
    description: Turn structured clauses into a compliant summary with clause references.
    input: the dict returned by retrieve_policy.
    output: >
      A summary string grouping the 10 critical clauses under their section
      headings, each prefixed with [clause_id], plus a VERIFICATION footer listing
      how many of the 10 were preserved and naming any that are missing.
    error_handling: >
      If any critical clause is absent from source, it is rendered as
      [MISSING IN SOURCE — VERBATIM REQUIRED] and surfaced in the footer rather
      than silently dropped.
