# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content parsed into structured numbered sections.
    input:
      type: file_path
      format: String representing a relative or absolute path to a .txt policy document
    output:
      type: structured_sections
      format: Ordered list of objects each containing a clause number and its full verbatim text as read from the file
    error_handling:
      - If the file path does not exist or is not accessible, raise a FileNotFoundError and halt without returning partial content
      - If the file is not a .txt file or cannot be decoded as UTF-8 text, raise a FormatError and do not attempt parsing
      - If the file is empty, raise a ContentError indicating no policy content was found
      - If numbered sections cannot be detected in the file, return the raw text as a single unstructured block and emit a warning that clause-level validation will not be possible

  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a clause-referenced compliant summary preserving all obligations, conditions, and binding verbs.
    input:
      type: structured_sections
      format: Ordered list of objects each containing a clause number and verbatim clause text, as returned by retrieve_policy
    output:
      type: text_file
      format: Plain-text summary written to the configured output path where each entry is prefixed with its clause number and preserves all binding verbs and multi-condition obligations
    error_handling:
      - If the input list is empty or null, raise a ContentError and do not produce an output file
      - If any of the ten required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are absent from the input, raise a ClauseInventoryError listing the missing clause numbers and halt
      - If a clause cannot be summarized without dropping a condition or softening a binding verb, quote the clause verbatim in the output and append a FLAGGED label with a short reason
      - If scope bleed phrases are detected in any generated summary text (such as "as is standard practice", "typically in government organisations", or "employees are generally expected to"), raise a ScopeBleedError and reject the output before writing to disk
      - If multi-condition obligations are detected to have fewer conditions in the summary than in the source clause, raise a ConditionDropError identifying the clause number and the dropped condition
