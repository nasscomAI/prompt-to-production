# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

    output: [What does it return? Type and format.]
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name, section, and clause number.
    input: The policy document directory path or the default repository policy path.
    output: A structured document index containing parsed sections and clause text for each source file.
    error_handling: Raises an error if a document is missing or cannot be parsed into numbered sections and clauses.
    output: [Type and format]
  - name: answer_question
    description: Searches the indexed policy clauses and returns a single-source answer with citations or the exact refusal template.
    input: The parsed document index and a user question in plain text.
    output: One answer string that either cites one source document and section numbers or returns the refusal template.
    error_handling: Refuses when the answer is not covered, when multiple documents compete for the same claim, or when answering would require blending documents.
