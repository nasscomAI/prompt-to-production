# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file from the filesystem and returns its
      content as a list of structured, numbered sections — preserving every
      clause number, heading, and body text exactly as written.
    input: >
      A file path (string) pointing to a .txt policy document
      (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A list of section objects, each containing:
        - section_number (string): the clause number (e.g., "2.3", "5.2"),
        - section_heading (string): the section title (e.g., "ANNUAL LEAVE"),
        - section_body (string): the full verbatim text of the clause.
      All original whitespace, binding verbs, and punctuation are preserved.
    error_handling: >
      If the file path is invalid, the file is empty, or the file does not
      contain identifiable numbered clauses, return an error message with
      the reason (e.g., "File not found", "Empty file", "No numbered
      clauses detected"). Never return a partial or guessed structure.

  - name: summarize_policy
    description: >
      Takes the structured sections produced by `retrieve_policy` and
      generates a clause-complete, faithful summary with clause reference
      numbers, preserving all binding verbs and multi-condition obligations.
    input: >
      A list of section objects as returned by `retrieve_policy` (each
      containing section_number, section_heading, and section_body).
    output: >
      A plain-text summary file written to the designated output path
      (e.g., summary_hr_leave.txt). The summary must:
        - Include one entry per numbered clause from the source,
        - Prefix each entry with its clause reference number (e.g., "2.3:"),
        - Preserve all binding verbs exactly (must, will, requires, may,
          not permitted),
        - Retain every condition in multi-condition obligations (e.g.,
          Clause 5.2 must name BOTH Department Head AND HR Director),
        - Contain zero information not present in the source text,
        - Flag any clause quoted verbatim with
          [VERBATIM — summarisation would alter meaning].
    error_handling: >
      If the input section list is empty or malformed, refuse to produce
      a summary. Return an error message stating the issue (e.g., "No
      sections provided", "Malformed section object — missing
      section_number"). Never generate placeholder or assumed content.
