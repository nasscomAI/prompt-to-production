# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for fast lookup.
    input: >
      doc_dir (str) — path to the directory containing the 3 policy .txt files.
    output: >
      A dictionary keyed by document filename, where each value is a dictionary
      of section_number -> section_text. Also includes a flat index of all clauses
      with their document source for keyword searching.
    error_handling: >
      If any of the 3 expected files is missing, raises FileNotFoundError listing
      which files are missing. If a file cannot be parsed into sections, stores
      the raw text as a single section "0.0".

  - name: answer_question
    description: Searches the indexed documents for the answer to a user question. Returns a single-source answer with citation, or the exact refusal template.
    input: >
      question (str) — the user's natural language question.
      index (dict) — the document index from retrieve_documents.
    output: >
      A formatted answer string containing:
      - The answer text citing the source document and section number, OR
      - The exact refusal template if no document covers the question.
      Single-source enforcement: if matches are found in multiple documents,
      only the best single-document match is used.
    error_handling: >
      If the question is empty, returns "Please ask a question about the policy documents."
      If the question matches content in multiple documents equally, answers from the
      single document with the strongest match. Never blends across documents.
