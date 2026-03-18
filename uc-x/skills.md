# skills.md — UC-X Document QA System

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and section number for efficient retrieval and citation.
    input: List of file paths (strings) for the three policy documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt. Paths can be absolute or relative.
    output: Dictionary with document names as keys, where each value is a dictionary containing 'content' (full text string) and 'sections' (dictionary mapping section numbers to section text). Example structure: {'policy_hr_leave.txt': {'content': '...', 'sections': {'2.6': 'section text...'}}}. Returns indexed data ready for search.
    error_handling: If any file does not exist, raise FileNotFoundError listing missing files. If file cannot be parsed or lacks numbered sections, return error dict with 'error' key explaining which document has structural issues. Never proceed if all three documents cannot be loaded successfully.

  - name: answer_question
    description: Searches indexed documents for relevant information, returns a single-source answer with citation OR the exact refusal template if question is not covered.
    input: Dictionary containing 'documents' (indexed documents from retrieve_documents) and 'question' (string: user's question). Question should be a natural language query about policies.
    output: Dictionary with keys 'answer' (string: response text), 'source' (string: document name + section number if answered, or 'REFUSAL' if not covered), 'confidence' (string: 'HIGH' if clear single-source answer, 'REFUSAL' if not covered). Answer must include inline citation in format: '[Answer] (Source: policy_[name].txt, section X.Y)' or exact refusal template.
    error_handling: If documents dict is empty or malformed, return error explaining missing data. If question is ambiguous between multiple documents with conflicting info, use refusal template rather than blending. If no relevant section found in any document, use exact refusal template. Never return uncited claims or hedged responses.
