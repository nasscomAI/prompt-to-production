# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes content by document name and section number for fast lookup.
    input: file_paths (list of str) — paths to policy .txt files
    output: dict mapping document_name -> {metadata: dict, sections: dict mapping section_number -> section_text}
    error_handling: If a file is not found, log error and continue with remaining files. If no files load successfully, raise RuntimeError. Each document must have at least one numbered section.

  - name: answer_question
    description: Searches indexed documents for the best matching section, returns single-source answer with citation OR exact refusal template.
    input: question (str), indexed_docs (dict from retrieve_documents)
    output: str — answer with citation (document name + section number) OR exact refusal template if question is not covered
    error_handling: If no matching section found, return exact refusal template. If multiple documents match, pick the most relevant single source and note that other documents may have related but separate policies. Never blend.
