skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections for faithful summarisation.
    input: >
      File path to a plain-text policy document (e.g.
      ../data/policy-documents/policy_hr_leave.txt).
    output: >
      Structured list/map of numbered sections and clauses (e.g. 1.1, 2.3, 5.2),
      each with its full source text and section heading; no paraphrasing at
      this stage.
    error_handling: >
      If the path is missing, unreadable, empty, or the file has no numbered
      clauses, raise a clear error and refuse to continue — do not invent
      sections or fall back to other documents. Do not silently skip malformed
      clauses; surface them so summarize_policy can flag or quote them.

  - name: summarize_policy
    description: >
      Takes structured numbered sections and produces a compliant summary with
      clause references, preserving every binding obligation and all conditions.
    input: >
      Structured numbered sections from retrieve_policy (clause id + full text
      per clause).
    output: >
      Plain-text summary written for summary_hr_leave.txt: every binding clause
      present with its clause number; multi-condition rules intact (including
      5.2 dual approvers); binding verbs preserved; verbatim quotes flagged
      when meaning would otherwise be lost.
    error_handling: >
      If any required binding clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2,
      5.3, 7.2) is absent from the structured input, refuse to emit a complete
      summary and report which clauses are missing (clause omission). If a
      clause cannot be shortened without dropping a condition or softening
      obligation language, quote it verbatim and flag
      [VERBATIM — meaning loss risk]. Reject and strip any draft language that
      adds non-source content (scope bleed) or hedges binding verbs (obligation
      softening). Never invent approval paths, timelines, or entitlements not
      in the source.
