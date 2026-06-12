skills:

- name: retrieve_documents
  description: Loads all three policy documents and indexes their contents by document name and section number for retrieval.
  input:
  type: list
  format: - "../data/policy-documents/policy_hr_leave.txt" - "../data/policy-documents/policy_it_acceptable_use.txt" - "../data/policy-documents/policy_finance_reimbursement.txt"
  output:
  type: indexed_document_collection
  format:
  document_name:
  section_number: section_content
  error_handling:
  - "If a file is missing, unreadable, or empty, return a document loading error identifying the affected file."
  - "If section numbers cannot be identified, return a document indexing error and do not create a partial index."
  - "Do not infer, reconstruct, or generate missing document content."
  - "Do not merge content across documents during indexing."
  - "Do not create synthesized sections or inferred section numbers."

- name: answer_question
  description: Searches the indexed policy documents and returns either a single-source answer with citation or the required refusal template.
  input:
  type: string
  format: "Natural-language policy question."
  output:
  type: string
  format:
  answer: "Answer supported by exactly one document with document name and section number cited for every factual claim."
  refusal: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
  error_handling:
  - "If the question is not covered by any document, return the refusal template exactly with no variation."
  - "If answering requires combining information from multiple documents, return the refusal template."
  - "If document evidence is ambiguous or insufficient, return the refusal template."
  - "Do not use hedging phrases including: while not explicitly covered, typically, generally understood, or it is common practice."
  - "Do not infer information that is not explicitly present in a document section."
  - "Do not drop, weaken, or generalize conditions, limits, approvals, prohibitions, dates, or requirements stated in the source."
  - "Do not return answers containing claims from more than one document."
  - "If a factual claim cannot be cited with document name and section number, return the refusal template."
  - "For the personal-phone/work-files question, answer only from policy_it_acceptable_use.txt section 3.1 or return the refusal template if ambiguity exists."
