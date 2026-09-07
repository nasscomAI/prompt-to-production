skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes content by document filename and section number.
    input: Path to directory containing policy documents.
    output: Dict mapping document filenames and section numbers to section titles and body text.
    error_handling: Raises FileNotFoundError if any of the 3 policy documents are missing.

  - name: answer_question
    description: Searches indexed policy documents for relevant sections, returning a single-source answer with exact document and section citations, or the exact refusal template if unaddressed.
    input: Question string and indexed documents dict.
    output: Answer string containing single-source factual content with citation, or exact refusal template.
    error_handling: Refuses with exact refusal template if question is unmentioned, vague, or creates cross-document blending ambiguity.
