# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from disk, parses it into structured numbered
      sections and clauses, and returns the content as a list of section objects
      each containing their clause entries.
    input: >
      A file path (string) pointing to a .txt policy document.
    output: >
      A list of dictionaries, each representing a section with keys:
        - section_number (str): e.g. "1", "2", "3"
        - section_title (str): e.g. "PURPOSE AND SCOPE", "ANNUAL LEAVE"
        - clauses (list[dict]): each clause with:
            - clause_id (str): e.g. "2.3", "5.2"
            - text (str): the full clause text as written in the source
            - binding_verb (str or None): the obligation verb if present
              (must, will, requires, may, not permitted, cannot)
    error_handling: >
      If the file is not found or unreadable, print an error message and
      exit with a non-zero status code. If a line cannot be parsed into
      a clause, include it as free text under the current section.

  - name: summarize_policy
    description: >
      Takes the structured section/clause list from retrieve_policy and
      produces a compliant summary that preserves every clause, every
      condition, every binding verb, and every deadline/value from the
      source document. Outputs the summary as a text file.
    input: >
      The structured list of sections and clauses from retrieve_policy,
      plus an output file path.
    output: >
      A .txt file at the output path containing the summary, organised by
      section with clause references. Each clause summary must either:
        (a) faithfully condense the clause preserving all conditions, or
        (b) quote the clause verbatim with a [VERBATIM] flag if condensation
            would lose meaning.
    error_handling: >
      If a clause has no identifiable obligation or content, include it
      with a note: "[INFO — no binding obligation in this clause]".
      Never skip a clause silently.
