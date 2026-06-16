# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns its content as an ordered list of numbered sections, preserving all clause numbers, binding verbs, and multi-condition structures exactly as written.
    input: >
      A single file path as string:
        - file_path — absolute or relative path to a .txt policy document
          (e.g. ../data/policy-documents/policy_hr_leave.txt)
    output: >
      An ordered list of dicts, one per detected numbered clause, each containing:
        - clause_id (string) — e.g. "2.3", "5.2"
        - heading (string) — the clause title if present, else ""
        - body (string) — the full clause text, verbatim, including all conditions
          and binding verbs (must, will, requires, not permitted)
      Also returns a top-level metadata dict:
        - document_name (string) — filename only
        - total_clauses (int) — count of numbered sections detected
    error_handling: >
      If file_path does not exist: raise FileNotFoundError with the path.
      If the file is empty: raise ValueError("Policy document is empty").
      If no numbered clauses are detected: return the full document text as a single
      clause with clause_id "UNNUMBERED" and log a warning — do not silently return
      an empty list.

  - name: summarize_policy
    description: Takes the structured clause list from retrieve_policy and produces a clause-complete summary that preserves all conditions, binding verbs, and multi-approver obligations without adding any information not in the source.
    input: >
      The output of retrieve_policy:
        - clauses (list of dicts) — each with clause_id, heading, body
        - document_name (string) — used in the output header
    output: >
      A plain-text summary string structured as:
        - One summary line per clause, prefixed with the clause_id
        - Binding verbs (must, will, requires, not permitted) preserved exactly
        - Multi-condition clauses (e.g. 5.2: Department Head AND HR Director) must
          name every condition — no collapsing to generic "approval required"
        - If a clause cannot be summarised without meaning loss: output the verbatim
          clause body and append the marker: [VERBATIM — MEANING LOSS RISK]
      Written to output file summary_hr_leave.txt.
    error_handling: >
      If clauses list is empty: raise ValueError("No clauses to summarise").
      If any clause body is empty: include the clause_id in the summary with the
      marker [EMPTY CLAUSE — REVIEW SOURCE] and continue — do not skip it silently.
      Never omit a clause from the output even if it cannot be summarised cleanly.
