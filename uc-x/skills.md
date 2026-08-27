skills:
  - name: retrieve_documents
    description: >
      Loads all three policy text files and indexes their content by document name
      and section number for single-source retrieval.
    input: >
      File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt (plain text policy documents with numbered
      sections).
    output: >
      Indexed document store mapping document filename and section number to section
      text, ready for lookup by answer_question.
    error_handling: >
      If any policy file is missing or unreadable, raise a clear file error and do not
      proceed with partial indexing. If a section number cannot be parsed, skip
      malformed sections but log which document failed parsing — never silently treat
      missing sections as empty policy. Do not merge sections across documents during
      indexing.

  - name: answer_question
    description: >
      Searches the indexed policy documents and returns a single-source answer with
      citation or the exact refusal template when the question is not covered.
    input: >
      One natural-language staff question (string) plus the indexed document store
      from retrieve_documents.
    output: >
      Either a single-source answer string with document name and section number cited
      for every factual claim, or the refusal template verbatim when the question is
      not covered or answering would require blending two documents.
    error_handling: >
      If the question is empty, ask the user to rephrase. If no matching section exists
      in any document, return the refusal template exactly with no variations. If
      multiple documents appear relevant, select the single best-matching section from
      one document only — never blend HR, IT, and Finance content into one answer.
      If HR and IT both seem relevant to the same question (e.g. personal phone for work
      files from home), answer from IT section 3.1 only or refuse — do not merge policies.
      Never use hedging phrases (while not explicitly covered, typically, generally
      understood, it is common practice). When a section has multiple required conditions,
      include every condition — do not drop approvers or prohibitions.
