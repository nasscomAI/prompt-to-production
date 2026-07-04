skills:
 - name: retrieve_documents 
   description: Loads all three policy files located at ../data/policy-documents/ and indexes them by document name and subsection number for lookup. 
   input: None. Always loads all three files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt. 
   output: A dictionary mapping document_name -> { subsection_number: (subsection_text, section_heading) } for all subsections found in each file. error_handling: If a file is missing or unreadable, throw an error with missing file name and the path where te file(s) was expected. Do not proceed with partial data.

 - name: answer_question 
   description: Given a user question, searches the indexed documents and returns a single-source answer with document name and section citation, or the exact refusal template if no match can be made without blending.
   input: A plain-text question string and the indexed document structure from retrieve_documents.
   output: Either (a) a string containing the answer text with source document name and section number, or (b) the exact refusal template verbatim. error_handling: If the question matches content in multiple documents at equal confidence, refuse rather than blend. If no match is found, return the refusal template exactly — no variations. Provide a clear error if the document index is missing or empty.