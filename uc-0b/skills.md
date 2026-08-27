skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the '.txt' policy document (string).
    output: A structured object mapping clause numbers to their exact text content.
    error_handling: If the file is not found or cannot be read, raise a clear error indicating the file path is invalid. If parsing fails, fall back to returning the raw text with a warning flag.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references, ensuring no meaning loss or dropped conditions.
    input: Structured document sections (e.g., JSON mapping clause numbers to text).
    output: A summarized text document with explicit clause references for each point.
    error_handling: If any multi-condition obligation cannot be summarized without ambiguity, quote it verbatim and flag it in the output instead of summarizing. If requested clauses are missing from the input, explicitly state their absence.
