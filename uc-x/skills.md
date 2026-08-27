skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes them by document name and section number.
    input: An optional list of string paths to the policy documents.
    output: A dictionary mapping (document_name, section_number) to the raw text content of the section.
    error_handling: Raise FileNotFoundError if any of the target files are missing, or ValueError if any document cannot be parsed into sections.

  - name: answer_question
    description: Searches indexed documents to find the relevant section matching the user's query, returning a single-source answer with document name and section citation, or the exact refusal template.
    input: A tuple containing (indexed_documents, query_string).
    output: A string containing either the direct answer with the cited document name and section number, or the exact refusal template if the answer is not present or involves cross-document blending.
    error_handling: Returns the exact refusal template if the query is not covered, ambiguous, or requires blending.
