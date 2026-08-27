skills:
  - name: retrieve_policy
    description: Load a plain-text policy file and parse it into a list of numbered sections, each containing its numbered sub-clauses.
    input: >
      path (str) to a .txt file whose structure is:
        - Section header lines: `\d+\. TITLE IN CAPS`
        - Sub-clause lines:     `\d+\.\d+ text ...`
        - Continuation lines:   indented, no clause number
        - Separators:           lines of ═, blank lines
    output: >
      list of dicts with keys:
        section_num (str, e.g. "2"),
        section_title (str, e.g. "ANNUAL LEAVE"),
        clauses (list of dicts with keys clause_num (str, e.g. "2.3") and text (str, full clause text with continuation lines joined by single space)).
      Order preserved from source.
    error_handling: >
      Missing file → raise FileNotFoundError. Empty file → return []. Malformed
      line (looks like a clause but does not match X.Y pattern) → skipped with
      no crash. A clause with no text after its number → included with text=""
      and marked so downstream can flag it verbatim.

  - name: summarize_policy
    description: Convert parsed sections into a structured summary that preserves every clause number and every binding verb from the source.
    input: >
      sections (list of dicts, output of retrieve_policy) and
      source_text (str, the original file contents, used for verification of no-external-phrase rule).
    output: >
      str containing the summary. Format:
        # Policy Summary — <derived from first section title or filename>
        ## Section X. TITLE
        - [X.Y] <clause text>
        - [X.Y] [VERBATIM] <clause text>   (when clause could not be safely condensed)
        ...
        ## Verification
        Clauses preserved: N of N
        Critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2): PRESENT / MISSING [list]
        Binding verbs preserved: PASS / FAIL [list any missing]
    error_handling: >
      Empty sections list → return a summary body with "No clauses parsed" and
      Verification: 0 of 0. Any critical clause missing from input → include a
      MISSING line in Verification, do not raise. Never invent clause text.
