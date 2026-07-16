skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: "file_paths (list[str], the 3 policy .txt paths)"
    output: "list of dicts: [{doc, clause, text}], one entry per numbered clause across all 3 documents"
    error_handling: >
      If a file is missing or unreadable, raise a clear error naming that file rather than
      silently indexing only the documents that did load — an incomplete index must not be
      used to answer questions as if it were complete.

  - name: answer_question
    description: Searches the indexed documents for a question and returns a single-source cited answer or the refusal template.
    input: "question (str), index (list[dict] from retrieve_documents)"
    output: "dict: {answer: str, source: 'doc §clause' or null, refused: bool}"
    error_handling: >
      If the best-matching content is spread across two documents with comparable relevance
      (no single document clearly dominates), treat this as a blending risk and return the
      refusal template rather than the best partial match. If no document matches at all,
      return the refusal template. Never fabricate a section number that does not exist.
