skills:
  - name: retrieve_documents
    description: Loads all three policy files from disk and indexes their content by document name and section number for citation-aware retrieval.
    input:
      type: list
      format: List of three file paths to plain-text policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output:
      type: dict
      format: Dictionary mapping document name to a dict of section numbers and their text content — e.g. {"policy_hr_leave.txt": {"2.6": "Employees may carry forward..."}}
    error_handling: >
      Aborts with a clear error if any of the three policy files cannot be found or read.
      Warns if a file contains no detectable numbered sections, as this may indicate
      a format issue. Never proceeds silently with a partially loaded document set.

  - name: answer_question
    description: Searches the indexed policy documents for a single-source answer to a staff question and returns it with a citation, or issues the exact refusal template if the question is not covered.
    input:
      type: object
      format: Dictionary with keys — question (string from user), index (dict from retrieve_documents output).
    output:
      type: string
      format: Either a cited answer in the format "According to [document name], section [X.X]: [answer text]" — or the exact refusal template if no answer is found.
    error_handling: >
      If the question matches content in more than one document, answers from the
      most specific document only and does not blend — never combines claims across documents.
      If the question is not found in any document, issues the exact refusal template
      with no variations or hedging phrases.
      Never returns an answer without a document name and section number citation.
      Forbidden phrases that trigger automatic refusal of the generated answer:
      "while not explicitly covered", "typically", "generally understood",
      "it is common practice", "it can be inferred".