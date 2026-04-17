# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      File path to a plain-text policy document
      (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A list of structured sections, each containing:
        - section_number: The clause number as it appears in the document (e.g., "2.3", "5.2").
        - heading: The section heading if present.
        - body: The full text of the clause.
        - binding_verb: The primary obligation verb (must, will, requires, not permitted, may, are forfeited).
    error_handling: >
      If the file cannot be read or is empty, return an error message and
      halt — do not produce a summary from missing data. If a section cannot
      be parsed into a numbered structure, include it as-is with a
      [PARSE_WARNING] flag and continue processing remaining sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-faithful summary with section references and preserved obligations.
    input: >
      A list of structured sections as returned by retrieve_policy, each with
      section_number, heading, body, and binding_verb.
    output: >
      A summary text file where each entry contains:
        - The clause number reference (e.g., "Clause 2.3").
        - A concise summary preserving the core obligation, all conditions, and the exact binding verb.
        - [VERBATIM] tag if the clause was quoted verbatim due to meaning-loss risk.
      The summary must contain exactly as many clause entries as the source
      document. No clauses may be omitted or merged.
    error_handling: >
      If a clause contains multi-condition obligations that risk being
      simplified, quote the clause verbatim and tag it [VERBATIM — meaning
      loss risk] rather than risk dropping a condition. Never silently omit a
      clause — if summarisation fails for any clause, include the original
      text with a [SUMMARISATION_FAILED] flag.
