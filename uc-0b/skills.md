# skills.md — UC-0B Policy Summarizer
# Refined from the RICE draft. Two skills, per UC-0B requirements.

skills:
  - name: retrieve_policy
    description: >
      Load a policy .txt document and return its content as structured numbered
      sections with per-clause text.
    input: >
      path: filesystem path to a policy .txt file.
    output: >
      dict {section_num: {"title": <section title>, "clauses": {clause_num: text}}}.
      Clause numbers are like "2.3"; multi-line clauses are joined into one string.
    error_handling: >
      Unnumbered heading lines and separator lines are ignored. A clause whose
      number does not belong to the current section is skipped. Missing file
      raises FileNotFoundError.

  - name: summarize_policy
    description: >
      Take the structured policy sections and produce a compliant summary that
      references every numbered clause and preserves every condition.
    input: >
      sections: dict produced by retrieve_policy.
    output: >
      A single multi-line string. One summary line per clause, prefixed by the
      clause number, grouped by section, plus a coverage line. Truthful and
      lossless by construction.
    error_handling: >
      Refuses (SystemExit) if any parsed clause lacks an authored summary
      (rule 1 - clause omission), if the token-preservation check fails for a
      clause (that clause is then output verbatim and flagged [VERBATIM]),
      or if any scope-bleed phrase appears in the output (rule 3 - invented
      information).