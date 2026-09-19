skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections and clauses.
    input: >
      Path to a UTF-8 .txt policy file (string). Expected layout: a document
      header, section headings of the form "N. TITLE" between rule lines, and
      clauses of the form "N.M text", with wrapped continuation lines indented.
    output: >
      Dict with: header (document title, reference, version lines) and
      sections, an ordered list of {number, title, clauses}, where each clause
      is {id: "N.M", text: full clause text with wrapped lines joined into one
      line}. No text is dropped or reworded during parsing.
    error_handling: >
      If the file is missing, unreadable, or empty, raise an error and stop; do
      not return partial content. If no numbered clauses are found, raise an
      error stating the file does not look like a numbered policy. If clause
      numbers are duplicated or out of sequence, keep every clause in file
      order and report a warning rather than silently merging or dropping any.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant clause-by-clause summary with clause references, preserving every obligation and condition.
    input: >
      The structured output of retrieve_policy (header plus ordered sections of
      {id, text} clauses).
    output: >
      Plain-text summary: document header, then each section heading followed by
      one line per clause in the form "[N.M] summary text". Clauses that fail
      validation are output as a verbatim quotation with the flag
      [VERBATIM - meaning-loss risk]. Also returns a validation report (clauses
      in source, clauses in summary, flagged clauses, critical-clause check).
    error_handling: >
      Validate each clause summary against its source clause: all numbers and
      key terms must be present, binding verbs must not be weakened, no number
      may appear that is absent from the source, and no banned scope-bleed
      phrase may appear. If any check fails, or no summary rule exists for the
      clause, fall back to the verbatim source text and flag it. If the final
      clause count does not match the source count, refuse to write the output
      file. Never drop a condition, never soften a verb, never add outside
      information.
