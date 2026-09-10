# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all 3 policy files, index by document name and section number
    input: None (uses fixed paths to the three policy files)
    output: dict with keys: documents (dict mapping doc_name -> full_text), sections (dict mapping (doc_name, section_num) -> section_text), doc_names (list of 3 doc names)
    error_handling: If any policy file is missing, raise FileNotFoundError with which file. If a file is empty, raise ValueError. Log warning if section parsing finds fewer sections than expected.

  - name: answer_question
    description: Search indexed documents for question, return single-source answer with citation OR exact refusal template
    input: question (str), sections (dict from retrieve_documents)
    output: dict with keys: answer (str), source_doc (str or None), source_section (str or None), is_refusal (bool)
    error_handling: If question is empty, return refusal. If multiple documents contain relevant info, return refusal (do not blend). If no relevant section found, return refusal template exactly.