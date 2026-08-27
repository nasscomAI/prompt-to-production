skills:
  - name: retrieve_documents
    description: Load and index all UC-X policy files by document name and section number.
    input: >
      Base directory path (string). Expected files:
      policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      Dictionary keyed by file name, each value containing raw text and parsed
      sections [{section_number, section_text}].
    error_handling: >
      If any required file is missing or unreadable, stop execution and raise a
      clear error naming the missing file.

  - name: answer_question
    description: Return a single-source, cited answer from indexed documents or the exact refusal template.
    input: >
      User question (string) and indexed documents (dictionary from retrieve_documents).
    output: >
      Either "answer + source citation" where all claims come from one document
      and include section number, or the refusal template verbatim.
    error_handling: >
      If question is empty, ambiguous across documents, lacks section evidence, or
      would require cross-document blending, return the refusal template exactly.
