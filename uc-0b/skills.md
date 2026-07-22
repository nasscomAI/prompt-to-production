skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered clauses grouped by section, using the document's own section headers and clause numbering as ground truth.
    input: path (str) to a policy .txt file with "N. SECTION TITLE" headers and "N.N " numbered clauses.
    output: list of dicts — {number, section, section_title, text} — one per parsed clause, whitespace-normalized.
    error_handling: If a section has no matching header line, section_title falls back to an empty string rather than raising; a file with zero matching clauses returns an empty list rather than crashing.

  - name: summarize_policy
    description: Takes the structured clauses from retrieve_policy and produces a compliant, section-grouped summary text with every clause referenced by number and reproduced verbatim (whitespace-normalized only) so no condition can be silently dropped or softened.
    input: list of clause dicts (as returned by retrieve_policy).
    output: str — the full summary text, grouped under "## N. SECTION TITLE" headings with one "- N.N: <clause text>" line per clause.
    error_handling: An empty clause list produces a header-only summary rather than raising; no clause is skipped or reordered relative to its source position.
