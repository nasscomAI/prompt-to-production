# skills.md — UC-0B Skills Definition

skills:
  - name: retrieve_policy
    description: Reads a plain text policy file and parses it into structured numbered sections and clauses.
    input: `input_path` (string path to .txt policy file).
    output: Data structure containing header metadata and list of numbered section/clause objects.
    error_handling: Raises FileNotFoundError if input path is invalid; warns if unnumbered text is encountered.

  - name: summarize_policy
    description: Takes structured policy clauses and produces a comprehensive summary enforcing clause completeness, exact verb retention, and multi-condition approval preservation.
    input: Structured policy sections and enforcement rules.
    output: Formatted string containing section-by-section summary retaining all numbered clauses.
    error_handling: Flags missing clauses or ambiguous phrasing with [VERBATIM] quotes to prevent obligation softening.

