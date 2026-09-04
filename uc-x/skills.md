skills:
  - name: retrieve_documents
    description: Loads the three policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes their content strictly by document filename and numbered section.
    input: file_paths (list of str paths to the 3 policy files).
    output: A validated document index mapping document filenames and section numbers to their parsed section titles and clause text.
    error_handling: Rejects missing, unreadable, empty, or malformed policy files with descriptive fatal errors.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source, section-cited answer, or returns the exact mandatory refusal template if ungrounded.
    input: query (str user question) and document_index (dict from retrieve_documents).
    output: str answer containing source filename + section number citations for every factual claim, or the exact character-for-character refusal template.
    error_handling: Refuses execution with the exact refusal template if no single document sufficiently supports the answer, if answering would require cross-document blending, or if the question is outside the scope of the policy documents.
