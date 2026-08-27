# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number for efficient lookup.
    input: >
      File paths to the three policy documents:
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      An indexed structure where each entry contains:
        - document_name: The source file name (e.g., "policy_hr_leave.txt").
        - section_number: The section/clause number (e.g., "2.6", "5.2").
        - heading: The section heading if present.
        - body: The full text content of the section.
      The index must cover every numbered section from all three documents.
    error_handling: >
      If any of the three files cannot be read, report which file(s) failed
      and continue loading the remaining files. Flag the missing document(s)
      so that answer_question can include a caveat when questions may relate
      to the unavailable document. If a section cannot be parsed, include it
      with a [PARSE_WARNING] flag and the raw text.

  - name: answer_question
    description: Searches the indexed documents for the most relevant section and returns a single-source answer with citation, or the refusal template if the question is not covered.
    input: >
      - question: A natural-language question string from the user.
      - document_index: The indexed structure returned by retrieve_documents.
    output: >
      One of two response formats:
        (a) Answer: A direct answer citing the source document name and section
            number (e.g., "Per policy_hr_leave.txt section 2.6, ..."). Every
            factual claim must be traceable to a single document and section.
            Multi-condition obligations must preserve all conditions.
        (b) Refusal: The exact refusal template — "This question is not covered
            in the available policy documents (policy_hr_leave.txt,
            policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
            Please contact [relevant team] for guidance."
    error_handling: >
      If the question matches sections in multiple documents, answer from the
      single most relevant document only — never blend. If genuine ambiguity
      exists between documents (e.g., IT and HR policies give conflicting
      guidance), use the refusal template and explain that the question
      spans multiple policies requiring human clarification. Never use
      hedging phrases or fabricate answers from general knowledge.
