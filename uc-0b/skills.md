skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and parses it into an ordered list of sections, each holding its numbered clauses.
    input: path (str) to a policy .txt file using the "N. SECTION TITLE" / "N.M clause text" numbering convention.
    output: list of {section_number, section_title, clauses: [{number, text}]} in document order.
    error_handling: Lines that are not a section header, clause, or continuation of the current clause (document title/version metadata) are skipped rather than misfiled.

  - name: summarize_policy
    description: Takes parsed sections and produces a clause-preserving summary — every clause verbatim under its section heading, so no condition can be silently dropped.
    input: list of sections as returned by retrieve_policy.
    output: str — formatted text with every section heading and every clause number + full clause text, in original order.
    error_handling: A section with no clauses (parse gap) is still printed with its heading so the omission is visible, not silently skipped.
