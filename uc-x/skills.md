# skills.md

INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: >
      Loads all 3 policy files, indexes by document name and section number.
      Returns a structured index of sections from each policy document.
    input: []
    output: >
      Dict mapping document names to their section indices.
      Format: {"policy_hr_leave.txt": {"1.1": "body text", "2.6": "body text", ...},
               "policy_it_acceptable_use.txt": {"1.1": "body text", "3.1": "body text", ...},
               "policy_finance_reimbursement.txt": {"1.1": "body text", "2.5": "body text", ...}}
    error_handling: >
      If any of the 3 required policy files is missing, raises FileNotFoundError
      with a clear message listing the missing file(s). Does not silently proceed
      with incomplete documentation.

  - name: answer_question
    description: >
      Searches indexed documents for a question, returns a single-source answer
      with citation OR the refusal template if the question is not covered.
      Never blends claims from multiple documents.
    input: >
      question (str): The policy question to answer.
      documents (dict): The indexed document output from retrieve_documents().
    output: >
      Tuple of (answer_text, source_doc, section_num) where:
      - answer_text is the matching section body text (or refusal template string)
      - source_doc is the document name (or None if refusing)
      - section_num is the section number (or None if refusing)
      If no good match is found, returns (refusal_template, None, None).
    error_handling: >
      If the documents dict is empty or malformed, returns the refusal template
      with None for source_doc and section_num. Never returns a blended answer
      combining sections from multiple documents.