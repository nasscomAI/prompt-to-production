# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Load a .txt leave-policy file and return its content as structured
      numbered sections for faithful summarisation.
    input: >
      input_path (string path to a UTF-8 .txt policy file, e.g.
      ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A structured object: document metadata (title, reference, version if
      present) plus an ordered list of sections; each section has a heading
      and a list of clauses, each with clause_id (e.g. "2.3") and text
      (exact source wording).
    error_handling: >
      If the file is missing, unreadable, or empty, raise a clear error and
      do not invent clauses. If the text has no numbered clauses (N.N
      pattern), raise an error describing the format problem rather than
      fabricating structure. Never silently drop a numbered clause during
      parse — every N.N block in the source must appear in the output list.

  - name: summarize_policy
    description: >
      Take structured policy sections and produce a compliant,
      clause-referenced summary that preserves obligations and conditions.
    input: >
      The structured sections object from retrieve_policy (metadata plus
      ordered sections with clause_id and exact text).
    output: >
      A plain-text summary written to the configured output path (e.g.
      summary_hr_leave.txt). Every source clause appears with its clause
      reference; multi-condition rules keep all conditions and binding verbs;
      clauses that cannot be shortened without meaning loss are quoted
      verbatim and marked [VERBATIM].
    error_handling: >
      If structured input is missing clauses, empty, or malformed, refuse to
      summarise and return/raise a clear error — do not invent policy text.
      If summarising a clause would drop a condition, deadline, dual approver,
      or binding verb, quote that clause verbatim and flag [VERBATIM] instead
      of softening or omitting. Never insert scope-bleed language not in the
      source. After producing the summary, the set of clause_ids in the
      output must match the set of clause_ids from retrieve_policy.
