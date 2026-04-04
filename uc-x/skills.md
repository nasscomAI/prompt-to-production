skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their contents by document name and section number.
    input: "List of file paths to UTF-8 .txt policy documents."
    output: "Dictionary keyed by document name containing ordered section objects with section number and full section text."
    error_handling: "If any file is missing, unreadable, empty, or cannot be parsed into numbered sections, return a clear error and do not continue with question answering."

  - name: answer_question
    description: Searches the indexed policy documents and returns either a single-source answer with document and section citation or the exact refusal template.
    input: "User question string and indexed document dictionary."
    output: "Plain-text answer grounded in one document section with citation, or the exact refusal template."
    error_handling: "If answering would require blending documents, if the question is not covered, if the best match is ambiguous, or if no single section supports the full answer, return the exact refusal template with no variation."