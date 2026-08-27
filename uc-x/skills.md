skills:
  - name: retrieve_documents
    description: >
      Loads all 3 policy files from disk, parses them into sections by
      heading, and returns an indexed structure keyed by document name
      and section number.
    input: >
      None (reads from hard-coded paths:
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt).
    output: >
      A dict mapping document_filename -> list of sections, where each
      section has keys: section_number, heading, content (list of lines).
    error_handling: >
      If a file is missing or unreadable, raise a clear FileNotFoundError
      listing which path could not be read.

  - name: answer_question
    description: >
      Accepts a user question and the indexed documents from
      retrieve_documents, searches for a single-source answer, and
      returns either a citation-grounded answer or the exact refusal
      template.
    input: >
      question (str), indexed_documents (dict as returned by
      retrieve_documents).
    output: >
      A string — either a factual answer with document filename and
      section number cited, or the verbatim refusal template.
    error_handling: >
      If multiple documents match (cross-document blend detected),
      refuse using the refusal template. If no document section matches,
      use the refusal template. Never return partial, guessed, or
      hedged output.
