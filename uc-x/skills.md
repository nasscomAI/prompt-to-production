# skills.md - UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy text files and indexes their content by document
      name and section number, making each section individually addressable for
      lookup by the answer_question skill.
    input: >
      A list of file paths (strings) - the three policy documents:
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A dict (the index) with structure:
        {
          "<document_filename>": {
            "<section_number>": "<full section text>",
            ...
          },
          ...
        }
      Each section is keyed by its dotted number (e.g. "2.6", "5.2") and contains
      the complete unmodified text of that section from the source file.
      Also returns a flat list of (doc_name, section_id, text) tuples for search.
    error_handling: >
      If any file cannot be read, raise FileNotFoundError naming the missing file.
      If a section cannot be parsed into a numbered section, store it under key
      "UNSTRUCTURED" so it is never silently lost. Log a warning for any file
      where zero numbered sections were found.

  - name: answer_question
    description: >
      Searches the indexed documents for sections relevant to the question and
      returns a single-source answer with citation, or the exact refusal template
      if the question is not covered in the documents.
    input: >
      Two arguments:
        - question (str)  - the employee's natural language question
        - index    (dict) - the document index returned by retrieve_documents
    output: >
      A dict with keys:
        - answer         (str)       - the answer text using only source document
                                       wording, followed by [Source: <filename>,
                                       Section <X.Y>], OR the exact refusal
                                       template if not found
        - source_doc     (str|None)  - the document filename the answer came from,
                                       None if refusal
        - source_section (str|None)  - the section number cited, None if refusal
        - is_refusal     (bool)      - True if the refusal template was returned
    error_handling: >
      If the question matches sections in more than one document and the sections
      cannot be answered from a single source without blending, set is_refusal=True
      and return the refusal template - never blend cross-document results.
      If the index is empty or None, raise ValueError: "Document index is empty -
      run retrieve_documents first." Never attempt to answer without a loaded index.
