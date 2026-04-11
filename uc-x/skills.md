# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, parses them into structured sections indexed by document name and section number.
    input: >
      A list of file paths (strings) pointing to the three policy documents:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
    output: >
      A document index — a dict keyed by document filename, each containing a list of
      section objects with:
        - section_number (string): e.g. "2.3", "5.2"
        - section_title (string): parent heading, e.g. "ANNUAL LEAVE"
        - content (string): full text of the clause
      Example: {"policy_hr_leave.txt": [{"section_number": "2.3", "section_title": "ANNUAL LEAVE", "content": "..."}]}
    error_handling: >
      If any file does not exist or cannot be read, report the missing file
      and continue loading the remaining files. If no files can be loaded,
      exit with an error.

  - name: answer_question
    description: Searches the indexed documents for relevant sections, returns a single-source answer with citation or the refusal template.
    input: >
      Two arguments:
        - doc_index (dict): The document index from retrieve_documents
        - question (string): The user's question
    output: >
      One of two responses:
        (1) A factual answer string citing the source document and section number.
            Example: "Yes, you may carry forward up to 5 unused annual leave days.
            Any above 5 are forfeited on 31 December. [Document: policy_hr_leave.txt, Section 2.6]"
        (2) The refusal template: "This question is not covered in the available
            policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt,
            policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: >
      If the question matches content in multiple documents, answer from the single
      most relevant document only. Never blend answers across documents. If the
      question is genuinely ambiguous across documents, use the refusal template
      and explain why. Never hedge or speculate.
