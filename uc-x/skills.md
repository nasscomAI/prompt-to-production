# skills.md

skills:
  - name: retrieve_documents
    description: >
      Load the three approved CMC policy files and index their contents as
      discrete sections keyed by source document name and section number.
    input: >
      The configured paths for policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A collection of section records containing document_name,
      section_number, section_title, and exact section_text.
    error_handling: >
      Fail closed with a clear startup error if any approved file is missing,
      unreadable, or contains no numbered sections. Never silently omit a
      source or load an unapproved source.

  - name: answer_question
    description: >
      Find the strongest single-document support for a policy question and
      return a concise answer with a document-and-section citation, or the
      exact refusal template.
    input: >
      A non-empty natural-language question and the indexed section records
      returned by retrieve_documents.
    output: >
      Either an answer composed only from one directly relevant policy
      section (or adjacent, directly relevant sections in the same document)
      followed by citations in the form
      "[Source: <document_name>, section <number>]", or the exact refusal
      template from agents.md.
    error_handling: >
      Refuse when the question is empty, unsupported, ambiguous, below the
      retrieval confidence threshold, or requires claims from more than one
      document. Do not guess, hedge, or blend sources.
