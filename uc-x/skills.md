# skills.md

skills:
  - name: retrieve_documents
    description: >
      Load all three policy documents, parse them into sections indexed by document name
      and section number (e.g., "HR Policy, Section 2.6"), and return a searchable index.
    input: >
      Directory path (string) containing policy_hr_leave.txt, policy_it_acceptable_use.txt,
      and policy_finance_reimbursement.txt.
    output: >
      Dictionary with keys: 'documents' (dict mapping document name to full text),
      'sections' (dict mapping "Document Name, Section X.Y" to section text),
      'index' (list of all section keys for search). Example:
      {
        'documents': {'HR Policy': '...full text...', 'IT Policy': '...', 'Finance Policy': '...'},
        'sections': {'HR Policy, Section 2.6': '...section text...', ...},
        'index': ['HR Policy, Section 1.1', 'HR Policy, Section 1.2', ...]
      }
    error_handling: >
      If any document file is missing, raise FileNotFoundError listing which files are missing.
      If a document cannot be parsed (malformed sections), raise ValueError with document name.

  - name: answer_question
    description: >
      Search indexed documents for a question, return a single-source answer with citation
      and section number, or the refusal template if not found in any document.
    input: >
      Dictionary with keys: 'question' (string), 'indexed_docs' (output from retrieve_documents).
    output: >
      Dictionary with keys: 'answer' (string), 'source' (string or None), 'found' (bool).
      Example 1 (found):
      {'answer': 'Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.', 'source': 'HR Policy, Section 2.6', 'found': True}
      Example 2 (not found):
      {'answer': 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the Human Resources Department for guidance.', 'source': None, 'found': False}
    error_handling: >
      Never return a blended answer citing two documents. If matching text appears in multiple
      documents, return the FIRST exact match only. If no exact match, return the refusal template.
      Do not hedge, suggest, or infer. Do not summarize or paraphrase — return exact quotations
      from the document. Do not drop conditions (e.g., "permanent WFH only", "Grade B and above").
