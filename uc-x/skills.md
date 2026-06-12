skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files, indexes their content by document name and section number, returning a searchable document store.
    input: doc_paths (list of str — paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output: dict mapping document_name (str) to sections (dict mapping section_number str to section_text str); raises error if any document is missing
    error_handling: If any file is not found, raise FileNotFoundError listing the missing file; if a file is empty, raise ValueError; print confirmation of each loaded document and section count to stdout on startup

  - name: answer_question
    description: Searches the indexed documents for an answer to the user's question, returns a single-source answer with citation or the exact refusal template — never blends across documents.
    input: question (str — the user's natural language question), document_store (dict as returned by retrieve_documents)
    output: str — either a direct answer with citation "[document_filename, Section X.Y]" or the exact refusal template if not covered or if cross-document blending would be required
    error_handling: If the question matches content in more than one document and combining them creates a claim not in either document alone, return the refusal template; never return a partial answer; never use hedging language
