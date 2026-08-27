# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: >
      A file path (string) pointing to a .txt policy document.
    output: >
      A list of structured sections, each containing:
        - section_number (string): The section number (e.g. "2", "3.2", "5").
        - section_title (string): The section heading (e.g. "ANNUAL LEAVE").
        - clauses (list): Each clause with its number, full text, and binding verb
          (must / will / requires / may / not permitted / are forfeited).
    error_handling: >
      If the file does not exist or is unreadable, raise an error with a
      descriptive message. If a clause cannot be parsed into a clean number +
      text structure, include it as-is with a parsing_warning flag. Never
      silently drop unparseable content.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: >
      A list of structured sections as returned by retrieve_policy.
    output: >
      A text summary where each source clause is represented with:
        - Clause reference prefix (e.g. §2.3).
        - A concise summary preserving the binding verb and all conditions.
        - [VERBATIM] flag and full quote if the clause cannot be shortened
          without meaning loss.
      The summary is grouped by section with section headings preserved.
    error_handling: >
      If a clause contains multiple conditions (e.g. two approvers, two
      deadlines), emit a MULTI_CONDITION check to verify all conditions appear
      in the summary. If a binding verb would be altered during summarisation,
      preserve the original verb verbatim. Never drop conditions silently.
