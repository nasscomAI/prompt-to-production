# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for retrieval.
    input: directory_path (str) — path to the directory containing the three policy .txt files.
    output: A dictionary mapping document names to sections, where each section is keyed by section number and contains the section text. Also stores the full text of each document.
    error_handling: If any policy file is missing, raise FileNotFoundError with the missing filename. If a file has no numbered sections, return full text with a warning. If a section number appears in multiple files, store both with document name prefix.

  - name: answer_question
    description: Searches indexed documents for a question answer, returns a single-source answer with citation OR the refusal template if the question cannot be answered from a single document.
    input: question (str), documents (dict) — the indexed documents from retrieve_documents.
    output: A dictionary with keys: answer (str), source_document (str), section_number (str), or refusal (bool) with refusal_template (str) if the question is not covered.
    error_handling: If question is empty, return refusal with template. If documents are empty, return refusal with template. If the answer spans multiple documents, return refusal with template rather than blending.
