# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Load a plain-text policy file and parse it into structured numbered sections and clauses.
    input: >
      A file path to a .txt policy document with numbered sections (e.g. 1, 2, 3)
      and numbered clauses (e.g. 1.1, 2.3, 5.2), separated by section headers.
    output: >
      An ordered list of sections, each containing: section_number, section_title,
      and a list of clauses. Each clause has: clause_number and clause_text
      (the full original text of the clause).
    error_handling: >
      If the file does not exist or is unreadable, raise FileNotFoundError with a
      clear message. If the file contains no recognizable numbered clauses, return
      an empty structure and log a warning.

  - name: summarize_policy
    description: Produce a clause-complete, faithful summary of a parsed policy document, preserving all obligations, conditions, and binding verbs.
    input: >
      The structured output from retrieve_policy: an ordered list of sections,
      each with section_number, section_title, and list of clauses (clause_number
      + clause_text).
    output: >
      A plain-text summary organized by section, where each clause is summarized
      in one or two sentences preserving all conditions, thresholds, and binding
      verbs. Clauses that cannot be shortened without meaning loss are quoted
      verbatim with a [VERBATIM] prefix. The summary ends with a clause count
      confirming all clauses are accounted for.
    error_handling: >
      If the input structure is empty or malformed, produce a summary containing
      only a warning: "No clauses found in input — unable to generate summary."
      Never fabricate content for missing clauses.
