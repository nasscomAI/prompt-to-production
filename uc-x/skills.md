# skills.md — UC-X Policy Document Q&A

skills:
  - name: retrieve_documents
    description: Loads all three policy text files and indexes content by document name and section number for efficient retrieval.
    input: List of file paths (strings) to the three policy documents - policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dictionary with document names as keys, each containing structured sections with section numbers and clause text. Structure: {'policy_hr_leave.txt': {'sections': [{'number': '2.3', 'title': 'ANNUAL LEAVE', 'text': '...'}]}, ...}. Returns indexed content ready for question answering.
    error_handling: If any of the three required files does not exist or is not readable, raises FileNotFoundError listing which files are missing. If files are empty or do not contain recognizable section structure, raises ValueError. Does not attempt to proceed with partial document set - all three files must load successfully.

  - name: answer_question
    description: Searches indexed policy documents for answer to user question, returns single-source answer with citation OR exact refusal template if question not covered.
    input: Dictionary with keys 'documents' (indexed documents from retrieve_documents) and 'question' (user's natural language question string).
    output: Dictionary containing 'answer' (string with either cited answer or refusal template), 'source_document' (document name if answer found, null if refused), 'section' (section number if answer found, null if refused), and 'answer_type' ('citation' or 'refusal'). Answer text includes citation format 'According to [document] section [X.X]: [content]' for citations, or exact refusal template for refusals.
    error_handling: If question is ambiguous or could be answered from multiple documents with conflicting information, uses refusal template rather than attempting to blend. If document structure is missing required fields, raises ValueError. If question is completely unrelated to policy topics (e.g., 'what is the weather'), uses refusal template with appropriate team suggestion. Never raises errors for legitimate policy questions - either answers with citation or refuses with template.
