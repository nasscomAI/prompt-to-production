# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections, preserving clause hierarchy and numbering exactly as written.
    input: >
      A file path (str) to a plain-text policy document (e.g., policy_hr_leave.txt).
    output: >
      A list of structured sections, each containing:
        - section_number (str): The clause number (e.g., "2.3", "5.2").
        - heading (str): The section heading, if any.
        - body (str): The full text of the clause, preserved verbatim.
      Clause count is reported so the summarizer knows the total to cover.
    error_handling: >
      If the file does not exist or cannot be read: return an error message
      and do not proceed. If the file contains no recognizable numbered
      clauses: return the raw text and flag "No structured clauses detected."

  - name: summarize_policy
    description: >
      Takes structured policy sections and produces a compliant summary
      that covers every clause, preserves all conditions and binding verbs,
      and references clause numbers throughout.
    input: >
      A list of structured sections from retrieve_policy, each with
      section_number, heading, and body.
    output: >
      A plain-text summary file with:
        - One summary point per source clause, prefixed with clause number.
        - All multi-condition obligations fully preserved.
        - Binding verbs kept exactly as in the source.
        - A trailing count: "Clauses covered: X / Y" to verify completeness.
      Any clause quoted verbatim is flagged with [VERBATIM — meaning loss risk].
    error_handling: >
      If a clause cannot be summarised without meaning loss: quote it verbatim
      and flag it rather than omitting or distorting it. Never silently drop
      a clause. Never soften obligations to avoid complexity.
