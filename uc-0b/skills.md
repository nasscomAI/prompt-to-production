# skills.md — UC-0B Policy Summary Agent

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a UTF-8 plain-text policy document whose clauses are numbered "X.Y" and grouped under numbered section headings.
    output: Ordered list of sections, each {number: str, title: str, clauses: [{id: str, text: str}]}, with wrapped clause lines joined into single strings; document reference/version captured in the header block.
    error_handling: Missing or unreadable file aborts the run with a clear error and no partial output; unrecognised non-blank lines are preserved inside their section rather than discarded, so no source text is silently lost.

  - name: summarize_policy
    description: Produces a clause-referenced summary in which every clause keeps its complete obligation.
    input: The structured sections returned by retrieve_policy.
    output: Plain-text summary containing one entry per source clause ("X.Y: ...") in document order plus a coverage count; clauses carrying multiple conditions are retained verbatim and flagged "[VERBATIM]" rather than paraphrased.
    error_handling: Never omits or merges clauses and never rewords binding verbs; if any clause cannot be processed, the run aborts naming that clause instead of writing an incomplete summary.
