skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes their content by document name and section number.
    input: A list of file paths (list of str) pointing to the three policy documents.
    output: A dict keyed by document filename, each value being a list of section dicts with keys section_id (str) and text (str).
    error_handling: Raises FileNotFoundError if any file is missing; skips malformed lines with a warning; returns empty section list for any document with no recognisable numbered clauses.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to the user's question, returning the answer with citation or the exact refusal template.
    input: question (str), index (dict from retrieve_documents).
    output: A str — either "Source: <doc> | Section <id>: <answer text>" or the exact refusal template if no single section covers the question.
    error_handling: If multiple documents match with equal confidence, applies single-source rule by selecting the highest-scoring section only; if no section scores above the threshold, returns the refusal template without hedging.
