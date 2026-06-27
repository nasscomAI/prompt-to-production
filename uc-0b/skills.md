skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and parses it into structured sections.
    input:
      type: file_path
      format: Plain text path to policy_hr_leave.txt
    output:
      type: structured_sections
      format: Dictionary mapping section numbers to clause strings
    error_handling: >
      Fail if the file is missing, empty, or unreadable. If clause formatting is ambiguous,
      raise an error rather than parsing incorrectly. Do not add external knowledge or modify content.

  - name: summarize_policy
    description: Generates a concise summary preserving all binding clauses, conditions, and references.
    input:
      type: structured_sections
      format: Dictionary of section numbers and clause strings
    output:
      type: summary_document
      format: Plain text summary referencing each clause number
    error_handling: >
      Raise an error if any of the 10 ground-truth clauses are omitted, softened, or have conditions dropped (especially Clause 5.2).
      Refuse to generate the summary if there is any scope bleed or outside assumptions.
      If a clause cannot be compressed without meaning loss, quote it verbatim.