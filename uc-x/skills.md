# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input:
      type: List of file paths
      format: [String] (paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output:
      type: Indexed document collection
      format: Object mapping {document_name: {section_number: section_text}}
    error_handling: >
      If any file is missing, unreadable, or not in the expected format, returns an error specifying the issue and does not proceed with indexing.

  - name: answer_question
    description: Searches the indexed documents for an answer to the user's question, returning a single-source answer with citation or the refusal template verbatim.
    input:
      type: Object
      format: { question: String, indexed_documents: Object }
    output:
      type: Answer object
      format: { answer: String, citation: {document_name: String, section_number: String} | null }
    error_handling: >
      If the question is not covered in any document, returns the refusal template exactly as specified. If multiple documents match, refuses to blend and returns the refusal template. If the input is ambiguous or malformed, returns an error and requests clarification.
