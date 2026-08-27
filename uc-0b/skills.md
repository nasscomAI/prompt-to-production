# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns it as structured numbered sections.
    input: path to the policy .txt file.
    output: >
      An ordered list of (section_number, section_title, [(clause_number, clause_text), ...]).
      Multi-line clauses are joined into a single clause_text.
    error_handling: >
      Box-drawing separators and preamble lines are ignored. Lines that are neither a
      section header nor a numbered clause are attached as continuation of the current
      clause, so no obligation text is lost.

  - name: summarize_policy
    description: Turns structured sections into a clause-complete, source-faithful summary.
    input: the structured sections returned by retrieve_policy.
    output: >
      A summary string with one bullet per numbered clause. Binding clauses are quoted
      verbatim and tagged [VERBATIM]; a completeness check line confirms all required
      clauses are present.
    error_handling: >
      If any required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is
      absent, emit an explicit COMPLETENESS WARNING listing the missing clauses rather
      than silently returning an incomplete summary. Never invents text to fill a gap.
