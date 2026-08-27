# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections, preserving the original hierarchy and clause numbering.
    input: file_path (string, path to a .txt policy document).
    output: A structured representation of the document with each numbered section identified, containing section_number (string), title (string), and body (string with full clause text).
    error_handling: >
      If the file does not exist or is unreadable, raise a clear error with the file path.
      If the document has no recognizable numbered sections, return the full text as a single section flagged with [UNSTRUCTURED — manual review needed].
      Never silently discard content that cannot be parsed into sections.

  - name: summarize_policy
    description: Takes structured numbered sections from a policy document and produces a compliant summary that preserves every clause, all conditions, and all binding obligations with clause references.
    input: A list of structured sections (from retrieve_policy output), each with section_number, title, and body.
    output: A text summary with one entry per clause, each referencing the source clause number, preserving all conditions, binding verbs, and numeric values. Clauses that cannot be safely summarised are quoted verbatim with a flag.
    error_handling: >
      If a section body is empty, include the section number with a note [EMPTY CLAUSE — check source document].
      If a multi-condition clause is detected, verify all conditions are preserved before outputting — if any condition might be lost, quote verbatim.
      Never produce a summary shorter than 60% of the original clause count — if the output is suspiciously short, flag missing clauses.
