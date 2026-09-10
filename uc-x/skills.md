skills:

* name: "retrieve_documents"
  description: "Loads all three policy documents and indexes their content by document name and section number."
  input:
  type: "file_set"
  format: "Three text files: policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
  output:
  type: "object"
  format: "Indexed policy collection keyed by document name and section number, containing only the source text and its document/section metadata."
  error_handling:
  invalid_input: "Reject the operation if any required policy file is missing, unreadable, empty, or cannot be indexed."
  indexing_failure: "Do not return a partial index as complete; report the affected document or section."
  cross_document_blending: "Keep each document and section separately addressable so claims can be traced to exactly one source document."
  condition_preservation: "Index complete section content so limits, conditions, exceptions, requirements, and prohibitions are not silently dropped."

* name: "answer_question"
  description: "Searches the indexed policy documents and returns a single-source answer with citation or the exact refusal template when the question is not covered."
  input:
  type: "object"
  format: "Object containing a user question and the indexed policy documents from retrieve_documents."
  output:
  type: "string"
  format: "Either a factual answer supported by one policy document with document name and section number cited for every factual claim, or the exact refusal template: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
  error_handling:
  invalid_input: "Reject the operation if the question is empty or the required document index is unavailable."
  uncovered_question: "Return the exact refusal template with no wording variations when the question is not covered by the available documents."
  cross_document_blending: "Never combine claims from different documents into one answer; if an answer requires combining documents or creates genuine ambiguity across documents, return the exact refusal template."
  hedged_hallucination: "Never use hedging phrases such as "while not explicitly covered", "typically", "generally understood", or "it is common practice"; use the refusal template instead when the documents do not directly support the answer."
  missing_citation: "Reject or regenerate any factual answer that does not cite the source document name and section number for every factual claim."
  condition_dropping: "Preserve all relevant limits, conditions, exceptions, requirements, and prohibitions from the cited section."
  personal_phone_question: "For questions about using a personal phone to access work files from home, return only a single-source IT policy answer supported by section 3.1 or the exact refusal template; never blend IT and HR claims."
