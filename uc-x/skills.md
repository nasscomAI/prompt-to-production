skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files, parses them into structured sections with numbered clauses, and returns a flat index of every clause tagged with its source document name and section number.
    input: None (loads from hardcoded relative paths to the 3 policy files).
    output: List of dicts with keys "doc", "clause_num", "section_num", "section_title", "text", "section_text", "full_ref".
    error_handling: Returns an error if any of the 3 files cannot be read or parsed. Does not fall back to a subset of documents.

  - name: answer_question
    description: Takes a user question and the document index, tokenizes the question into keywords, scores every clause (weighting clause-level matches double section-level matches), detects cross-document ambiguity, and returns either a single-source cited answer or a refusal message.
    input: "question" (string), "index" (list of clause dicts from retrieve_documents).
    output: String — either a cited answer "[doc_name section X.Y] clause text" or a refusal message (cross-document warning or not-covered template).
    error_handling: Returns the exact refusal template if no relevant clause is found. Returns a cross-document ambiguity warning if top-scoring clauses span multiple documents. Never blends answers from multiple documents.
