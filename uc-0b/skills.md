# skills.md — UC-0B Policy Summary Agent

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and returns it as structured numbered sections ready for clause-by-clause processing.
    input: >
      One path — path to a .txt policy file whose body consists of numbered
      clauses (e.g. "2.3 ...") grouped under section headings separated by
      decorative rule lines.
    output: >
      Dict — { title: str, reference: str, version: str,
               clauses: [ { clause_id: str (e.g. "2.3"),
                            section_title: str,
                            text: str (clause text, line wraps collapsed) } ] }
      Header fields are "" when absent from the file.
    error_handling: >
      If the file is missing or unreadable, exit non-zero with a clear error —
      there is nothing to summarize. Non-clause lines (headings, decorative
      rules) become section_title only, never clause text. If a clause number
      is duplicated or out of sequence, keep every occurrence and append
      [SEQUENCE_CHECK] to the affected clause_id rather than silently
      dropping text.

  - name: summarize_policy
    description: Turns structured policy clauses into a compliant summary that preserves every clause reference, condition and binding verb.
    input: >
      The dict returned by retrieve_policy (header metadata plus the list of
      clause dicts).
    output: >
      Plain-text summary — one short entry per clause, each entry beginning
      with its clause_id, preserving all conditions and binding verbs; any
      clause that could not be safely paraphrased is quoted word-for-word and
      marked [VERBATIM]. Ends with a coverage line listing the count of
      clauses included.
    error_handling: >
      Never drop a clause silently: if a paraphrase would lose a condition
      (dual approvals, deadlines, thresholds, absolutes), quote the clause
      verbatim and flag it instead. Never invent content to fill gaps; if a
      clause dict is empty or malformed, emit its clause_id with [UNREADABLE]
      and continue. Raise only when the clause list itself is empty.
