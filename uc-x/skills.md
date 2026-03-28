# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for efficient lookup.
    input: >
      A list of file paths (strings) pointing to the three policy documents:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
    output: >
      A document index (dictionary) keyed by document filename, where each
      document contains:
        - doc_ref (string): The document reference code (e.g. HR-POL-001).
        - title (string): The document title.
        - sections (dict): Keyed by section number (e.g. "3.1"), containing
          the full clause text and any binding verbs or conditions.
    error_handling: >
      If any file does not exist or is unreadable, raise an error with the
      specific filename. If a section cannot be parsed, include it as raw text
      with a parsing_warning. Never silently skip a document or section.

  - name: answer_question
    description: Searches the indexed documents for relevant sections, returns a single-source answer with citation or the refusal template.
    input: >
      Two parameters:
        - question (string): The employee's question in natural language.
        - doc_index (dict): The document index from retrieve_documents.
    output: >
      One of two responses:
        (a) An answer containing:
          - source_document (string): The filename of the source document.
          - section_ref (string): The section number cited (e.g. "§3.1").
          - answer_text (string): The factual answer citing specific words from
            the source section, with all conditions preserved.
          - [If multiple documents are relevant] Separate answer blocks per
            document — never a blended answer.
        (b) The exact refusal template:
          "This question is not covered in the available policy documents
          (policy_hr_leave.txt, policy_it_acceptable_use.txt,
          policy_finance_reimbursement.txt). Please contact [relevant team]
          for guidance."
    error_handling: >
      If the question matches sections from multiple documents, present each
      document's answer separately — never blend. If no section matches, use
      the refusal template verbatim. Never use hedging phrases or invent
      information not present in the indexed documents.
