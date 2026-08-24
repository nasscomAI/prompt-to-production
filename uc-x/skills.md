skills:
  - name: retrieve_documents
    description: Reads and parses the three policy text files, indexing their sections and clauses by document name and section number.
    input: None.
    output: dict mapping document filenames and section keys to section text.
    error_handling: Raises FileNotFoundError if any of the three policy files are missing.

  - name: answer_question
    description: Takes a query, matches it against indexed content, and returns a cited single-source answer or the verbatim refusal template.
    input:
      question: str query from the user.
      indexed_docs: dict containing parsed sections.
    output: str answer containing factual response + citation OR the verbatim refusal template.
    error_handling: Refuses to output speculative answers. If a question bridges multiple documents in a conflicting/blending way, it must refuse or answer from a single source only.
