skills:
  - name: retrieve_documents
    description: Load all three policy files and index their content by document name and section number.
    input: Paths to the three policy document files.
    output: Structured index mapping each document name and section number to its full clause text.
    error_handling: Reject missing or unreadable files; never invent missing policy content.

  - name: answer_question
    description: Search indexed documents for relevant sections matching the question, return a single-source cited answer or the refusal template.
    input: User question string and the document index.
    output: Answer citing document name and section number, or the exact refusal template if not found.
    error_handling: If matches span multiple documents, answer from the single most relevant document only; never blend. If no match found, use refusal template.
