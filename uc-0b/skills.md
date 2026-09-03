skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text (.txt) policy file and returns its content as a
      structured mapping of numbered clause references to their verbatim text.
    input: >
      A single file path (str) to a plain-text policy document such as
      ../data/policy-documents/policy_hr_leave.txt. The document contains
      numbered clauses of the form n.n (e.g. 2.3, 5.2) along with separate
      section headings.
    output: >
      An ordered structure (dict/list) mapping each detected clause number
      (e.g. "2.3") to its exact verbatim text as it appears in the source,
      with subsection clause text joined on a single line. Only clause numbers
      actually present in the source are returned.
    error_handling: >
      If the file does not exist, cannot be read, is empty, or contains no
      numbered clauses in the expected n.n format, raise a clear error that
      reports the path and the problem. Do not guess clause text, do not
      fabricate clause numbers, and do not return a partial or silently
      truncated parse when a clause cannot be located.

  - name: summarize_policy
    description: >
      Takes the structured clause map from retrieve_policy and produces a
      compliant summary that references all ten required clauses while
      preserving every condition and every binding obligation, quoting
      verbatim and flagging any clause that cannot be condensed losslessly.
    input: >
      A structured clause map (dict of clause number -> verbatim text), the
      set of the ten required clause numbers (2.3, 2.4, 2.5, 2.6, 2.7, 3.2,
      3.4, 5.2, 5.3, 7.2), and the output file path where the summary is
      written.
    output: >
      A plain-text summary file at the given path containing one entry per
      required clause, each prefixed by its clause number. Each entry states
      the core obligation while preserving EVERY condition of the source
      clause and the binding force of words like must, requires, will, and not
      permitted. Clause 5.2 must explicitly name BOTH the Department Head and
      the HR Director and state that manager approval alone is not sufficient.
      If any required clause cannot be condensed without losing meaning, its
      source text is quoted verbatim and flagged with a visible review marker.
    error_handling: >
      If any of the ten required clause numbers is missing from the input
      clause map, do not invent its content: emit the clause reference with a
      review flag noting the clause could not be located in the source. If no
      input is provided or the map is empty, write an error message to the
      output indicating the summary could not be produced, rather than
      fabricating a summary. Never add information not present in the source
      text and never weaken an obligation.
