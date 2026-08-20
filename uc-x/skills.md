# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name and section number into a searchable clause index.
    input: list of file paths (str) to the policy .txt documents
    output: list of dicts with keys doc, section, text, searchable, header
    error_handling: Raises SystemExit with a clear message if any file is missing; tolerant of decorative separators and multi-line clauses.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source verbatim answer with citation, or the exact refusal template when the question is not covered.
    input: question (str) and the clause index from retrieve_documents
    output: str — either "Source: <doc> (Section <n>)\n<verbatim clause>" or the exact refusal template
    error_handling: Low-confidence matches (below threshold) return the refusal template rather than hedging; answers are always confined to a single document.