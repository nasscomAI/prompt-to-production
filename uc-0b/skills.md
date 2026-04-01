skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and parses it into a structured format of numbered sections for precise clause mapping.
    input:
      type: file
      format: A .txt file path containing the source policy document.
    output:
      type: object
      format: A dictionary or JSON object mapping clause numbers to their exact text content.
    error_handling: Raises a file error if the path is invalid or empty; flags any sections that do not follow the expected numbering format for manual verification.
  - name: summarize_policy
    description: Transforms structured policy sections into a condensed summary while strictly preserving all obligations, multi-condition requirements, and original scope.
    input:
      type: object
      format: A structured collection of numbered policy sections.
    output:
      type: string
      format: A plain text summary containing every numbered clause with its core obligations and binding verbs intact.
    error_handling: Quotes clauses verbatim and applies a FLAG if summarization risks losing specific conditions; rejects any external "standard practice" terminology to prevent scope bleed; performs a validation check to ensure no clause from the ground truth inventory is omitted.