skills:
  - name: retrieve_documents
    description: Loads the three policy text files (HR, IT, and Finance) and indexes their sections and clauses by document name and section number.
    input: docs_dir (str path to directory containing policy documents)
    output: dict mapping document filenames to structured sections and clause mappings
    error_handling: Handles missing documents with informative error messages; parses text using robust section boundaries.

  - name: answer_question
    description: Queries indexed documents to retrieve a precise single-source answer with document name and section citations, or outputs the strict refusal template if uncovered.
    input: question (str), indexed_docs (dict)
    output: str representing the factual answer with exact citation, or the verbatim refusal template
    error_handling: Refuses cross-document blending; refuses ungrounded questions with standard refusal template; prevents hedging language.
