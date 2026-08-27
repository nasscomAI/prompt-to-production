# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy document files and indexes their content by document name and section number for efficient retrieval.
    input: Directory path (string) containing the policy document files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Dictionary with keys as document names (str) and values as nested dictionaries where each key is a section number (str like '2.3') and value is the section text content (str). Also includes 'metadata' with document references and versions. Structure: {'policy_hr_leave.txt': {'1.1': 'text...', '2.3': 'text...'}, 'metadata': {'policy_hr_leave.txt': {'reference': '...', 'version': '...'}}}
    error_handling: Returns None with error message if directory does not exist, required policy files are missing, or files cannot be parsed into numbered sections. Raises ValueError if no valid sections found in any document.

  - name: answer_question
    description: Searches indexed policy documents for relevant content and returns a single-source answer with explicit citation OR the refusal template if the question is not covered.
    input: Dictionary with keys 'question' (string - user's question), 'documents' (indexed documents from retrieve_documents), and 'refusal_template' (string - exact template to use when question not covered).
    output: Dictionary with keys 'answer' (string - the response text), 'source_document' (string - document name or 'NONE' if refusal), 'source_sections' (list of section numbers like ['3.1', '3.2'] or empty list if refusal), and 'citation' (string - formatted citation like '[policy_it_acceptable_use.txt section 3.1]' or empty string if refusal).
    error_handling: Returns refusal template if question cannot be matched to any document content. Never blends information from multiple documents - if multiple documents are relevant, chooses the most directly applicable single source or returns refusal. Never uses hedging language. If input documents are invalid or empty, returns error dictionary with 'error' key.
