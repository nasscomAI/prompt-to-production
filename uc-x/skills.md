# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy files and index their content by document name and section number for efficient lookup.
    input: >
      A list of file paths to the three policy .txt files. Each file has numbered
      sections and clauses in the format X.Y.
    output: >
      A dictionary keyed by document filename, where each value is a dict of
      section_number → clause_text. Also maintains a flat searchable index of
      all clause texts with their document and section references.
    error_handling: >
      If any file does not exist or is unreadable, raise FileNotFoundError naming
      the missing file. If a file has no recognizable clauses, include it in the
      index with an empty clause set and log a warning.

  - name: answer_question
    description: Search the indexed documents for the most relevant clause(s) to answer a user question, returning a single-source cited answer or the refusal template.
    input: >
      A user question string and the document index produced by retrieve_documents.
    output: >
      One of two response formats:
      (1) A factual answer citing [document_name, Section X.Y] for every claim,
      drawn from a single document only, preserving all conditions and thresholds.
      (2) The refusal template verbatim if the question is not covered.
    error_handling: >
      If the question is empty or unintelligible, return: "Please provide a
      specific question about CMC policy." If multiple documents are relevant but
      combining them would create a blended claim, answer from the single most
      relevant document and note that the other document may also be relevant
      without blending their content.
