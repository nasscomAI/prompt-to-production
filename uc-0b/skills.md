skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      A file path to a plain-text policy document (.txt), e.g.
      ../data/policy-documents/policy_hr_leave.txt.
    output: >
      Structured numbered sections (list of clause objects) where each section has a clause
      number/identifier (e.g. 2.3), its core obligation, and its binding verb (must, will,
      may / are forfeited, requires, not permitted), derived directly from the source text.
    error_handling: >
      If the file path does not exist or cannot be read, returns an error and does not
      fabricate content. If the text contains no numbered clauses, reports that the clause
      inventory could not be built and refuses to proceed rather than inventing sections.
      If a numbered clause's obligation or binding verb is ambiguous, it is kept verbatim
      and flagged rather than interpreted.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: >
      The structured numbered sections returned by retrieve_policy (clauses with numbers,
      core obligations, and binding verbs) plus the desired output path
      (e.g. uc-0b/summary_hr_leave.txt).
    output: >
      A summary written to the requested output path in plain text, where every numbered
      clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) appears with its clause
      reference, its full obligation (all conditions preserved, including clause 5.2's
      dual approval from Department Head AND HR Director), and its binding verb unsoftened.
    error_handling: >
      If any clause is missing from the input or a multi-condition obligation has lost a
      condition, refuses to write the summary and reports the omission. If a clause cannot
      be summarised without meaning loss, quotes it verbatim and flags it in the output. If
      any phrase not attributable to the source (e.g. "as is standard practice", "typically
      in government organisations") would enter the summary, drops it and marks the draft
      non-compliant. If the output path cannot be written, raises an error without guessing.