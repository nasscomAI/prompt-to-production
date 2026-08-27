# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

# skills.md — UC-X Policy Q&A Bot

skills:
  - name: retrieve_documents
    description: Loads all three CMC policy .txt files and returns content indexed
      by document filename and section number, ready for single-source lookup.
    input: >
      document_dir (str) — path to the policy-documents directory
      filenames (list of str) — [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
      ]
    output: >
      index (dict) mapping document_filename → dict of section_id → text
      e.g. index["policy_it_acceptable_use.txt"]["3.1"] = "Personal devices may be..."
    error_handling: >
      Missing file: logs warning and continues with remaining files; never crashes.
      Empty file: logs warning and skips that file.
      Encoding error: retries with latin-1 before logging and skipping.

  - name: answer_question
    description: Searches the indexed documents for the best single-source answer
      to a question and returns either a cited answer or the exact refusal template.
    input: >
      question (str) — employee's natural-language question
      index (dict) — output of retrieve_documents
    output: >
      response (str) — one of:
        (a) Single-source answer ending with:
              (Source: [filename], Section [X.X])
        (b) Exact refusal template if question is not covered or spans documents
              in a way that would create new implied permissions
    error_handling: >
      Empty question: returns "Please enter a question."
      Index is empty: returns refusal template with note that no documents were loaded.
      Multiple document matches that create cross-doc blend: returns refusal template.
