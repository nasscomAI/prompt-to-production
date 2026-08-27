# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy documents by document name and section number.
    input: "File paths to policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)"
    output: "Dictionary indexed by {document_name: {section_number: section_text}}; enables single-source lookups"
    error_handling: "If document file is missing, log error with file path and raise exception; if section index fails, return raw document text with warning"

  - name: answer_question
    description: Searches indexed policy documents for single-source answer, returns citation or refusal template.
    input: "User question (string) and indexed documents dictionary"
    output: "Object with {answer, source_document, section_number} if found; OR {refusal_template} if not covered or cross-document ambiguity detected"
    error_handling: "If question is ambiguous across multiple documents, return refusal template; if no match found, return refusal template; never blend or hedge"
