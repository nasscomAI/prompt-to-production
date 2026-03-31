skills:
  - name: retrieve_documents
    description: Loads all three designated policy documents and indexes their contents structurally by exact document name and section number.
    input:
      type: array
      format: A list of precise file paths encompassing the applicable HR, IT, and Finance policy files.
    output:
      type: object
      format: A structured text index mapping all clauses strictly to their exact source document and numbered sections continuously.
    error_handling: Halts startup if any required source file is missing or unreadable; if natural structural numbers are absent within the text, it refuses to hallucinate index numbers to permanently protect citation validity.
  - name: answer_question
    description: Interrogates the indexed documents to formulate a strictly accurate, single-source answer with citations or safely defaults to a static refusal template.
    input:
      type: string
      format: The raw textual user query submitted interactively via the CLI environment.
    output:
      type: string
      format: A factual declaration actively citing the distinct source document and section number, or the precisely unaltered refusal template.
    error_handling: Actively thwarts cross-document blending by enforcing single-source logic and resorting to the exact refusal template if answers span multiple documents; halts hedged hallucination by scanning for and rejecting assumed phrases like 'typically' or 'generally'; prevents condition dropping by mandating verbatim retention of multi-approval conditions before returning the output.
