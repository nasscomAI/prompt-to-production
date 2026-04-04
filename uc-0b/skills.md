skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its contents as structured numbered sections.
    input: "String path to a UTF-8 .txt policy file."
    output: "Ordered list of objects, each containing a clause number and its full clause text."
    error_handling: "If the file is missing, unreadable, empty, or not a valid .txt file, return a clear error and do not continue. If numbered sections cannot be reliably extracted, return an error instead of guessing."

  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a compliant summary with clause references.
    input: "Ordered list of clause objects with clause number and clause text."
    output: "Plain-text summary with one output line per clause, preserving clause references and all conditions."
    error_handling: "If any clause is missing, duplicated, malformed, or cannot be summarized without meaning loss, quote that clause verbatim and flag it. Reject summaries that introduce unsupported assumptions, scope bleed, or softened obligations."