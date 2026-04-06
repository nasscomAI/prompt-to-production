# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: >
      Loads the three corporate policy files (HR, IT, Finance) and indexes them by document name and section number.
    input: None.
    output: A collection of document objects containing section text and metadata (filename/section).
    error_handling: Log error and stop if any file (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) is missing.

  - name: answer_question
    description: >
      Searched indexed documents to provide a single-source answer with citations or the refusal template.
    input: Question string.
    output: Answer string with document name and section citation OR verbatim refusal template.
    error_handling: Use refusal template if the answer is not found or is ambiguous across sources.

