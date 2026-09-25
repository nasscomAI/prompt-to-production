# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files from ../data/policy-documents/ and indexes their content by document name and section number.
    input: >
      No user input required. Reads from fixed file paths:
      - ../data/policy-documents/policy_hr_leave.txt
      - ../data/policy-documents/policy_it_acceptable_use.txt
      - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A dictionary keyed by document name, where each value is a dictionary
      of section numbers mapped to their text content.
      Example: {"policy_hr_leave.txt": {"2.6": "Annual leave carry-forward..."}}
    error_handling: >
      If any file is missing or unreadable, raise an error naming the specific
      file. Do not silently skip documents — all 3 must load successfully.

  - name: answer_question
    description: Searches the indexed documents for content relevant to the user's question and returns a single-source answer with citation, or the exact refusal template.
    input: >
      A natural-language question string from the user, plus the indexed
      document data produced by retrieve_documents.
    output: >
      Exactly one of:
      (1) A factual answer citing one source document name and section number
          (e.g. "According to policy_hr_leave.txt, section 2.6: ..."), OR
      (2) The refusal template verbatim:
          "This question is not covered in the available policy documents
          (policy_hr_leave.txt, policy_it_acceptable_use.txt,
          policy_finance_reimbursement.txt). Please contact [relevant team]
          for guidance."
    error_handling: >
      If the question matches content in multiple documents, answer from
      the single most relevant document only — never blend. If genuine
      ambiguity exists across documents, use the refusal template.
