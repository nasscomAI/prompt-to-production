skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files and returns a searchable index organised by document name, section number, and clause number.
    input: doc_paths (dict mapping document filename to its file path on disk)
    output: dict keyed by document filename, each value a dict keyed by section number containing section title and a list of clause dicts (clause_num, text)
    error_handling: If a file is not found, print a warning and skip that document rather than crashing — but report which document was skipped so the caller knows coverage is reduced. If a section cannot be parsed, include its raw text as an UNPARSED entry rather than dropping it silently.

  - name: answer_question
    description: Searches the indexed documents for the most relevant single-clause answer to a question and returns it with a citation, or returns the refusal template if no relevant clause is found.
    input: question (string), index (dict as returned by retrieve_documents), threshold (int, minimum keyword match score to consider a clause relevant)
    output: string — either a cited answer in the format "[Source: <doc_name> — Section <N>: <title>, Clause <N.N>]\n\n<clause text>" or the exact refusal template
    error_handling: If the index is empty, return the refusal template. Never blend results from two documents — the top-scoring clause from a single document wins. If two documents score equally, return the refusal template rather than picking arbitrarily or blending.
