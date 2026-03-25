skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy files from disk, parses them into a
      structured index keyed by (document_filename, section_number), and
      stores the section text for lookup by answer_question.
    input: >
      List of file paths (strings) to the three policy documents:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
    output: >
      A dict mapping (doc_filename, section_number) → section_text (string).
      Example key: ("policy_hr_leave.txt", "2.6")
    error_handling: >
      If a file is missing or unreadable, raise FileNotFoundError with the
      filename. Do not proceed with a partial index — all three documents
      must load successfully before any question is answered.

  - name: answer_question
    description: >
      Searches the indexed documents for content relevant to the employee
      question. Returns a single-source answer with mandatory citation
      (document filename + section number), or the exact refusal template
      when no single document covers the question or when answering would
      require blending two documents.
    input: >
      question (string): the employee's natural-language query.
      index (dict): the structured index produced by retrieve_documents.
    output: >
      A string in one of exactly two formats:
      (a) Citation answer:
            "According to <doc_filename>, Section <X.Y>: <verbatim or
             closely paraphrased text from that section only>."
      (b) Refusal (verbatim, no variation):
            "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt,
            policy_finance_reimbursement.txt).
            Please contact [relevant team] for guidance."
    error_handling: >
      If the question matches content in more than one document and the
      documents do not say the same thing, the skill MUST return the
      refusal template — never blend or summarise across documents.
      If the index is empty or None, raise ValueError before attempting
      any lookup.
