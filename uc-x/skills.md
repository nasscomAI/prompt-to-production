skills:
  - name: retrieve_documents
    description: Loads all three approved policy files and indexes their content by document name and section number, making them available for single-source lookup.
    input: List of three absolute file paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) as strings.
    output: Nested dict indexed by document name, then section number, each entry containing the section heading and its verbatim text — e.g. {"policy_hr_leave.txt": {"5.2": {"heading": "...", "text": "..."}}}.
    error_handling: If any of the three files is missing or unreadable, raise a FileNotFoundError identifying the specific file and halt — do not proceed with a partial index. If a document contains no detectable section numbers, store its full raw text under a "UNPARSED" key and append a NEEDS_REVIEW warning so the caller knows structure could not be resolved.

  - name: answer_question
    description: Searches the indexed policy documents for a question and returns a single-source answer with an explicit document name and section citation, or the exact refusal template if the question is not covered.
    input: Question string from the user, plus the index dict returned by retrieve_documents.
    output: Dict containing answer_text (string — the verbatim relevant excerpt or refusal template), source_document (string — exact filename, or null on refusal), and source_section (string — exact section number, or null on refusal).
    error_handling: If the question matches content in more than one document, do NOT blend — either return the single most directly relevant section from one document only, or return the refusal template if cross-document ambiguity cannot be resolved without combining claims. If the question is not found in any document, respond with exactly the refusal template and no variation — "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance." Never use hedging phrases such as "while not explicitly covered", "typically", "generally understood", or "it is common practice" in any response.
