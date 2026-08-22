# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections for downstream summarisation.
    input: File path to a UTF-8 .txt policy document containing numbered clauses (e.g. `N.M` format) under section headings.
    output: >
      An ordered list of sections; each section has a section number, heading,
      and a list of clauses, where each clause is an object with
      {clause_number (str), text (str)} — text joined from wrapped lines with
      no content altered.
    error_handling: >
      If the file does not exist or cannot be decoded as UTF-8, fail with a
      clear error naming the path — do not proceed with partial content.
      If a line does not match the expected `N.M` clause pattern or a clause
      number is missing/duplicated, raise an error listing the offending
      lines; never guess at numbering.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary in which every critical clause appears with its full conditions intact and its clause reference cited.
    input: >
      Structured sections as produced by retrieve_policy — an ordered list of
      {section_number, heading, clauses:[{clause_number, text}]}.
    output: >
      Plain-text summary written to --output; every sentence traceable to one
      clause and tagged with that clause's number. Critical clauses
      (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must all be present.
      Clauses that cannot be summarised without meaning loss are quoted
      verbatim inside quotation marks and flagged [VERBATIM QUOTE].
    error_handling: >
      If any required clause would have to drop a condition to fit, emit it as
      a verbatim quote per agents.md instead of paraphrasing — never silently
      omit or soften. If a binding verb's strength cannot be preserved
      ("must", "requires", "not permitted"), refuse to paraphrase that clause.
      If the summary would contain a statement not traceable to a source
      clause, remove it before writing output. If the input contains none of
      the critical clauses, abort with an error rather than produce a summary
      of the wrong document.
