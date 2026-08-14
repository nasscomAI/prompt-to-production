skills:
  - name: retrieve_documents
    description: Loads all three policy document text files and indexes their content by document name and section number, preserving exact text for citation.
    input: List of three file paths (strings) pointing to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dictionary indexed by document name, then by section number, containing full text of each section. Example structure - {'policy_hr_leave.txt' - {'2.6' - 'Employees may carry forward...'}, 'policy_it_acceptable_use.txt' - {'3.1' - 'Personal devices may be used...'}}.
    error_handling: If any file not found, print which file is missing and exit. If file is empty, log warning but continue with other files. If section numbering cannot be parsed, store content by line number instead and flag for review. Never invent section content.

  - name: answer_question
    description: Searches indexed policy documents for relevant information to answer employee question, returns single-source answer with citation OR refusal template if not covered.
    input: Dictionary with (1) indexed documents from retrieve_documents, (2) user question string, (3) refusal template string.
    output: String containing either (A) factual answer from ONE document with format 'According to [Document] section [X.X], [answer]', OR (B) refusal template verbatim with appropriate [relevant team] filled in (HR Department, IT Department, or Finance Department based on question topic).
    error_handling: If multiple documents contain relevant information, choose the most specific one. If combining documents would be needed for complete answer, use refusal template instead. If question is ambiguous, ask for clarification rather than guessing. If no documents contain relevant information, use refusal template. Never use hedging phrases ('typically', 'while not explicitly covered') - either answer with citation or refuse cleanly.
