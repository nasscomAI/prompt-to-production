skills:
  - name: retrieve_documents
    description: Loads all three CMC policy text files into memory and indexes their content by document name and section number for downstream querying.
    input: >
      A list of three file paths (strings) pointing to:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
      Each file is a plain text document with sections marked by headings like
      '1. PURPOSE AND SCOPE', '2. ANNUAL LEAVE', etc.
    output: >
      A dictionary (document_index) where each key is the filename (string) and
      each value is a dictionary mapping section_number (string, e.g. '2.6') to
      section_text (string — the full text of that section). Example:
      {
        "policy_hr_leave.txt": {
          "2.6": "Employees may carry forward a maximum of 5 unused annual leave...",
          "5.2": "LWP requires approval from the Department Head and the HR Director..."
        },
        ...
      }
    error_handling: >
      If a file does not exist, raise FileNotFoundError with the missing filename.
      If a file cannot be parsed into sections, store the full file text under the
      key 'FULL_TEXT' and log a warning. Never return an empty index.

  - name: answer_question
    description: Takes a user question and a document index, searches for the answer in a single source document, and returns the answer with citation or the exact refusal template if not found.
    input: >
      Two arguments:
        question (string): the employee's natural-language policy question.
        document_index (dict): the index returned by retrieve_documents.
    output: >
      A string containing either:
        (a) The answer followed by a citation line:
            "Source: [filename], Section [section_number]"
        (b) The exact refusal template if the question is not in the documents:
            "This question is not covered in the available policy documents
            (policy_hr_leave.txt, policy_it_acceptable_use.txt,
            policy_finance_reimbursement.txt). Please contact the relevant team
            for guidance."
      No other output formats are permitted.
    error_handling: >
      If the LLM returns a response containing hedging phrases ('typically',
      'generally understood', 'while not explicitly covered', 'likely', 'usually'),
      discard the response and return the refusal template instead.
      If the LLM cannot be reached, return the refusal template with an appended note:
      '(System error — please try again or contact IT support.)'
      Never return an empty string. Never combine facts from two documents.
