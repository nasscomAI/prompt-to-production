# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy documents and indexes their content by document name and section number.
    input: >
      File paths to the three policy documents:
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      An indexed data structure mapping each (document_name, section_number) pair
      to its corresponding text content. Every section present in the source files
      must appear in the index. The index preserves document boundaries — sections
      from different documents are never merged or interleaved.
    error_handling: >
      If any of the three files does not exist or cannot be read, exit with a
      clear error message naming the missing file. Do not silently skip a
      document — all three must be loaded for the system to operate. If a
      document contains no parseable section headers, load it as a single
      section and log a warning.

  - name: answer_question
    description: Searches the indexed documents for the answer to a user question and returns a single-source answer with citation, or the refusal template.
    input: >
      A natural-language question string from the user, plus the indexed
      document structure produced by retrieve_documents.
    output: >
      Exactly one of two response formats:
        (a) A factual answer drawn from a single source document, with every
            claim citing the document name and section number
            (e.g., "policy_it_acceptable_use.txt section 3.1"). The answer
            must never combine claims from two different documents.
        (b) The refusal template, used verbatim:
            "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt,
            policy_finance_reimbursement.txt). Please contact [relevant team]
            for guidance."
    error_handling: >
      If the indexed document structure is empty or was not initialised, exit
      with an error message instructing the user to run retrieve_documents first.
      If a question matches content across multiple documents, answer from the
      single most relevant document only — never blend. If relevance is
      genuinely ambiguous between documents, return the refusal template rather
      than guessing. Never use hedging phrases such as "typically" or "generally
      understood" in any response.
