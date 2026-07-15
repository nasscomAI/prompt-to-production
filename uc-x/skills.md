# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files from disk, parses them into sections
      indexed by document name and section number, and returns a unified index
      ready for search.
    input: >
      A list of three file path strings:
        - "../data/policy-documents/policy_hr_leave.txt"
        - "../data/policy-documents/policy_it_acceptable_use.txt"
        - "../data/policy-documents/policy_finance_reimbursement.txt"
      All three must be loaded — partial loading is not permitted.
    output: >
      A dict (the document index) structured as:
        {
          "policy_hr_leave.txt": [
            { "section": "2.3", "text": "..." },
            ...
          ],
          "policy_it_acceptable_use.txt": [ ... ],
          "policy_finance_reimbursement.txt": [ ... ]
        }
      Each entry in the list is a dict with:
        - section (string): The section number (e.g. "3.1", "5.2").
        - text (string): The full text of that section, unmodified.
      Documents are identified by their basename (not full path) as the key.
    error_handling: >
      If any of the three files cannot be found or read: print an error message
      identifying which file failed and exit with code 1. Do not proceed with
      a partial index — all three documents must be loaded.
      If section numbers cannot be parsed from a document: include all text
      under section "UNPARSED" for that document and log a warning to stdout.
      Never silently discard content.

  - name: answer_question
    description: >
      Searches the document index for an answer to a natural-language question.
      Returns a single-source answer with citation, or the exact refusal template
      if no single document answers the question without cross-document blending.
    input: >
      A dict with keys:
        - question (string): The employee's natural-language question.
        - index (dict): The document index as returned by retrieve_documents.
    output: >
      A string: either
        (a) A direct answer ending with a citation in the format:
            "(Source: policy_[name].txt, Section [X.Y])"
            The answer text contains only claims verifiable in the cited section.
        (b) The exact refusal template:
            "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt,
            policy_finance_reimbursement.txt).
            Please contact [relevant team] for guidance."
            Where [relevant team] is replaced with "HR", "IT", or "Finance"
            if the question topic is determinable from context, else left as
            "[relevant team]".
    error_handling: >
      If the index is empty or missing a document: print a warning identifying
      which document is absent and return the refusal template — do not attempt
      to answer from an incomplete index.
      If the question string is empty or None: return the refusal template.
      If matching sections are found in more than one document and combining them
      would produce a new claim: return the refusal template, not a blended
      answer. Err on the side of refusal over blending.
      Never return an answer that contains hedging phrases: 'while not explicitly
      covered', 'typically', 'generally understood', 'it is common practice'.
      If the drafted answer contains any of these, discard it and return the
      refusal template instead.
