skills:
  - name: retrieve_documents
    description: Load all 3 policy files, parse into structured sections indexed by document name and section number.
    input: A list of 3 file paths to .txt policy documents.
    output: A dict mapping document filename to a list of sections, where each section has keys: section_number, heading, content (list of clause dicts with clause_id and text).
    error_handling: If any file is missing or unreadable, raise an error listing which file could not be loaded and do not proceed to answering.

  - name: answer_question
    description: Search indexed documents for the best single-source answer, return answer with citation or the verbatim refusal template.
    input: A question string and the indexed document structure (output of retrieve_documents).
    output: A dict with keys: answer (the response text), source (document name + section number), or refusal (boolean) if the question is not covered.
    error_handling: If the question matches content in multiple documents, return an answer from only one document (the most specific match) — never blend. If no document covers the question, return the exact refusal template with refusal: true.
