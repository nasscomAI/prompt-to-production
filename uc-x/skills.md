skills:
  - name: retrieve_documents
    description: Loads all three policy text files from disk, parses them into a section-indexed structure keyed by document name and section number, and returns the indexed corpus ready for querying.
    input: Directory path (string) pointing to the policy-documents folder containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Dictionary mapping document name → {section_number: section_text} so that any section can be looked up by document name and section number for exact citation.
    error_handling: Raise FileNotFoundError if any of the three required files are missing; raise ValueError if a file is empty or cannot be parsed into sections.

  - name: answer_question
    description: Searches the indexed corpus for a single-document, single-section answer to the user's question, then returns the answer with an explicit citation (document name + section number) or the exact refusal template if the question is not covered or spans multiple documents ambiguously.
    input: User question (string) and the indexed corpus returned by retrieve_documents.
    output: String containing either (a) the answer text followed by the citation in the format "[document_name §section_number]", or (b) the verbatim refusal template when no single-source answer exists.
    error_handling: If the corpus is empty or not provided, raise ValueError; if the question string is empty or whitespace-only, return a prompt asking for a valid question; on any I/O or parsing error, surface the error message to the user without guessing an answer.
