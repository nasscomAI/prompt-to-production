skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy documents and indexes each by
      document name and section number for exact lookup.
    input: >
      None (loads hard-coded paths:
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt).
    output: >
      A dictionary mapping document names to their parsed section
      contents (doc_name -> {section_number: full_text}).
    error_handling: >
      Raises FileNotFoundError if any policy file is missing.
      Silently skips sections with malformed headers.

  - name: answer_question
    description: >
      Searches indexed policy documents for a factual answer to the
      user's question, returning a single-source answer with
      citation, or the refusal template verbatim.
    input: >
      question (string) — the user's natural-language query.
      Optionally, the pre-loaded document index from
      retrieve_documents.
    output: >
      A single string — either (a) a factual answer citing exactly
      one source document and section number, or (b) the verbatim
      refusal template.
    error_handling: >
      If the question is ambiguous or no single document addresses
      it, returns the refusal template with no hedging or blending.
