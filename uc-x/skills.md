# skills.md — UC-X Ask My Documents (RAG Q&A)

skills:
  - name: retrieve_documents
    description: Loads all three CMC policy text files into memory and splits each into named sections.
    input: No arguments — paths are resolved relative to the script's data/policy-documents/ directory.
    output: Dict mapping doc_name (str) to dict with keys text (str), sections (list), filename (str).
    error_handling: Raises FileNotFoundError listing which policy file is missing if any of the three files cannot be found.

  - name: answer_question
    description: Keyword-searches loaded policy documents for the best matching section and returns a cited answer or the standard refusal.
    input: question (str), docs (dict from retrieve_documents), use_llm (bool, default False).
    output: Str answer beginning with '[Source: filename, Section X.Y]' if found, or exact refusal string if not found.
    error_handling: If docs is empty, returns the refusal template immediately; never raises an exception on a question it cannot answer — always returns the refusal string instead.
