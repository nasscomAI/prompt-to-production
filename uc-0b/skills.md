# skills.md -- UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from disk and returns its content as structured
      numbered sections, preserving the original clause numbering and section hierarchy.
    input: >
      A file path (str) pointing to a .txt policy document (e.g.,
      ../data/policy-documents/policy_hr_leave.txt). The file is plain text with
      numbered sections (e.g., 1. PURPOSE AND SCOPE, 2. ANNUAL LEAVE) and numbered
      sub-clauses (e.g., 2.1, 2.2, 2.3).
    output: >
      A structured representation of the policy document as a list of sections, where
      each section contains:
        - section_number (str): The top-level section number (e.g., "2")
        - section_title (str): The section heading (e.g., "ANNUAL LEAVE")
        - clauses (list): A list of clause dicts, each containing:
            - clause_number (str): The full clause number (e.g., "2.3")
            - clause_text (str): The complete, unmodified text of the clause
      All clause text must be preserved verbatim -- no truncation, paraphrasing, or
      modification during retrieval.
    error_handling: >
      If the file path does not exist or is not readable, raise a clear error with
      the file path and exit. If the file is empty or contains no recognisable clause
      structure, return an empty sections list and log a warning. Never silently
      return partial content -- if parsing fails for a section, include the raw text
      of that section with a [PARSE_WARNING] flag.

  - name: summarize_policy
    description: >
      Takes structured policy sections from retrieve_policy and produces a compliant
      summary that preserves every clause, every binding obligation, and every condition
      with clause-number references.
    input: >
      A structured list of sections as returned by retrieve_policy, containing
      section numbers, section titles, and clause dicts with clause_number and
      clause_text fields.
    output: >
      A plain-text summary string structured by section, where each entry:
        - References the source clause number (e.g., "Clause 2.3:")
        - Preserves the binding verb exactly as stated in the source (must, requires, will, not permitted)
        - Preserves ALL conditions in multi-condition obligations (e.g., Clause 5.2 must name both Department Head AND HR Director)
        - Contains no information not present in the source document
        - Flags any clause quoted verbatim with [VERBATIM -- cannot summarise without meaning loss]
      The output must cover all 10 key clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4,
      5.2, 5.3, 7.2) plus all other numbered clauses in the source.
    error_handling: >
      If a clause cannot be summarised without meaning loss (e.g., multiple interacting
      conditions where paraphrasing risks dropping one), quote the clause verbatim and
      flag it with [VERBATIM -- cannot summarise without meaning loss]. If the input
      sections list is empty or missing clause data, output a warning stating
      "No policy content available to summarise" and do not generate any summary text.
      Never invent or hallucinate policy content to fill gaps. If a section has zero
      clauses, note it as "[Section X: No clauses found]" rather than omitting it.
