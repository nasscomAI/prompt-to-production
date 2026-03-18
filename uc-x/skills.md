skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files and indexes their content by document name and section number for single-source retrieval.
    input: paths (list of str, paths to the three .txt policy files)
    output: dict mapping document filename to dict of section_number → section_text; also returns a flat list of (doc_name, section_number, section_text) tuples for search
    error_handling: Raises FileNotFoundError with document name if any file is missing; raises ValueError if a file cannot be parsed into numbered sections; never returns partial index silently

  - name: answer_question
    description: Searches the indexed policy documents for an answer to the user's question and returns either a single-source cited answer or the exact refusal template — never blending claims from two documents.
    input: question (str), index (dict from retrieve_documents), as keyword or positional arguments
    output: str — either a factual answer with citation in format "According to [doc_name], section [N.N]: [answer text]." OR the exact refusal template if the question is not covered; never a blended multi-document answer
    error_handling: If the question matches sections in two or more documents and cannot be answered from one document alone without meaning loss, returns the refusal template rather than blending; never raises an exception on a question — always returns a string
