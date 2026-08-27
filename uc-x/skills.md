# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files, parses them into structured sections indexed by document name and section number, and returns a searchable index for question answering.
    input: document_paths (list of strings, paths to the three policy .txt files).
    output: A structured index where each entry contains document_name (string), section_number (string), section_title (string), and content (string). The index supports lookup by document and section.
    error_handling: >
      If any file does not exist or is unreadable, raise a clear error identifying which file(s) failed.
      If a document has no recognizable section structure, index it as a single section flagged [UNSTRUCTURED].
      All three documents must be loaded successfully before answering questions — partial loading is not permitted.

  - name: answer_question
    description: Searches the indexed documents for content relevant to the user's question and returns either a single-source answer with citation or the refusal template.
    input: question (string, the user's natural language question) and document_index (structured index from retrieve_documents).
    output: Either an answer string with format "[Answer text]. [Source: document_name, Section X.X]" OR the refusal template "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: >
      If the question matches content in multiple documents, present each document's answer separately with its own citation — never merge into one statement.
      If the question is partially covered (some aspects answered, some not), answer what is covered with citations and explicitly state which aspects are not covered using the refusal template for those parts.
      If the question is ambiguous, ask the user to clarify rather than guessing which document to search.
      Never produce an answer without a section citation — if a section number cannot be identified, flag with [CITATION NEEDED — section unclear].
