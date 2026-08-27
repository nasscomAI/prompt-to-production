skills:
  - name: retrieve_documents
    description: Loads all 3 CMC policy .txt files and builds an index of sections, keyed by document name and section number, for fast single-source lookup.
    input: document_paths (list of str) — absolute or relative paths to the 3 policy files.
    output: A dict with document filenames as keys, each mapping to a dict of {section_number: section_text}. Also returns a flat index list of (doc_name, section_id, text) tuples for search.
    error_handling: If any file is not found, log a warning and continue with the remaining files — do not crash. If a file is empty, skip it and log a warning. An empty index (all files missing/empty) raises RuntimeError.

  - name: answer_question
    description: Searches the indexed documents for the best single-source answer to a natural language question, and returns a cited answer or the refusal template.
    input: question (str) — the employee's question. index (list of tuples) — output from retrieve_documents. documents (dict) — full sections dict from retrieve_documents.
    output: A formatted string containing either: (a) a single-source answer with citation "[Document Name, Section X.Y] — [fact]" or (b) the exact refusal template if the question is not covered or requires cross-document blending.
    error_handling: If keyword matching returns hits from more than one document with equal confidence (blending risk), issue the refusal template rather than guessing. Never return a blended answer. If the index is empty, raise RuntimeError("No documents loaded — cannot answer questions.").
