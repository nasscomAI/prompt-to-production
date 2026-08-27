skills:
  - name: retrieve_documents
    description: Loads and indexes the three policy documents (HR, IT, Finance) by document name and section number.
    input: List of file paths to policy documents (string list).
    output: Structured index mapping document names and section numbers to content (dictionary/object).
    error_handling: Reports missing or unreadable files and skips incorrectly formatted sections while logging a warning.

  - name: answer_question
    description: Searches the indexed documents for a query and returns a single-source answer with citations or the mandatory refusal template.
    input: User question string and the document index object.
    output: Answer string with document name and section number citation, or the exact refusal template if no match.
    error_handling: Refuses to blend multi-source content; if conflict causes ambiguity, it returns the mandatory refusal template.
