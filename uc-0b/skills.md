skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: String representing the file path to the .txt policy document.
    output: Structured data mapping clause numbers to their exact textual content.
    error_handling: If the file is not found, cannot be read, or lacks discernible numbered sections, return a clear error message refusing the operation.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with explicit clause references, maintaining all core obligations.
    input: Structured data mapping clause numbers to their content.
    output: A written summary document referencing each clause number and its summarized obligations.
    error_handling: If an output summary would drop a condition or change the meaning of a clause, it must inject the verbatim quote and flag it instead of providing an inaccurate summary.
