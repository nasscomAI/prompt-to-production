# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy text files and builds a searchable index keyed by document name and section number.
    input: >
      document_paths: list of three .txt file paths:
      policy_hr_leave.txt,
      policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      Indexed structure with:
      documents_by_name,
      sections as [{document_name, section_id, section_text}],
      and lookup maps for section-level retrieval.
      Includes parse diagnostics per document.
    error_handling: >
      If any file cannot be read, return explicit file-path read error.
      If section numbering cannot be parsed, retain raw text and include parse warning.
      Never fabricate missing sections.

  - name: answer_question
    description: Answers a policy question using one grounded source section with citation, or returns the exact refusal template if unsupported or ambiguous.
    input: >
      question: string,
      indexed_documents from retrieve_documents.
    output: >
      Either:
      single-source answer text where every factual claim cites document name + section number,
      or exact refusal template:
      This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance.
    error_handling: >
      If question requires blending two documents to produce a yes/no permission, refuse using the exact template.
      If no direct supporting section is found, refuse using the exact template.
      Reject answers containing prohibited hedging phrasing or uncited claims.
