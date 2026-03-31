# skills.md

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy documents from disk, parses them into sections,
      and builds an in-memory index keyed by document name and section number.
    input: >
      File paths to the three policy documents (list of strings):
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A structured index (dict) mapping each document name to its sections,
      where each section has a section number (e.g. "2.6") and its full text
      content. Example structure:
        { "policy_hr_leave.txt": { "2.6": "Leave carry-forward is limited to..." } }
    error_handling: >
      If any file path is missing or unreadable, raise a clear error naming
      the missing file. Do not silently skip documents — all three must load
      successfully or the skill must fail with an explicit message.

  - name: answer_question
    description: >
      Accepts a user question and the document index, searches for matching
      sections, and returns a single-source answer with a citation or the
      refusal template.
    input: >
      - question: string — the user's natural-language question.
      - document_index: dict — the structured index returned by retrieve_documents.
    output: >
      One of two formats:
        (a) A factual answer derived from exactly one document, ending with
            a citation in the format [document_name, Section X.Y].
        (b) The refusal template verbatim:
            "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt,
            policy_finance_reimbursement.txt). Please contact [relevant team]
            for guidance."
    error_handling: >
      - If the question matches content in multiple documents, answer from
        the single most relevant document only. If genuine ambiguity exists
        (no single document fully answers the question), return the refusal
        template.
      - If the question is empty or nonsensical, return the refusal template.
      - Never guess, speculate, or use hedging language. If the answer is not
        explicitly stated in a document section, treat it as not found.
