skills:
  - name: retrieve_documents
    description: Loads all three policy files, parses each into a list of numbered clause dicts, and returns a document index keyed by filename with document label and clause list.
    input: data_dir (Path) — directory containing the three policy .txt files
    output: dict keyed by filename, each value containing "label" (string) and "sections" (list of dicts with keys "clause" and "text"); prints loaded file names and clause counts to stdout
    error_handling: Prints a warning to stderr for any file that cannot be found; raises RuntimeError if no documents could be loaded at all; skips unnumbered lines silently (decorative borders and section headings are discarded, not treated as clauses).

  - name: answer_question
    description: Searches the indexed documents for clauses matching the employee question, returns a single-source answer with citation, or returns the exact refusal template if no document covers the question or if answering requires cross-document blending.
    input: question (string), index (dict from retrieve_documents)
    output: string — either a cited single-source answer in the format "[Label — Section X.Y]: <text>" or the exact refusal template; never a blend of two documents
    error_handling: Returns the refusal template when keyword score across all documents is below threshold (score < 2); returns the refusal template when two documents score within 60% of each other and the question cannot be cleanly attributed to one source; never raises an exception — always returns a string.
